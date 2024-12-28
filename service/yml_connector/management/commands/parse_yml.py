import hashlib
from types import NoneType

import requests
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from django.utils import timezone

from supplier.models import Supplier, SupplierProduct, Category
from report.models import Report, ReportError
from supplier.models import SupplierPriceSignature
from yml_connector.tasks import download_image_for_product
from yml_connector.models import XMLParsingRule, PriceReplacementRule

from yml_connector.management.commands.web_parser import parse_price_from_website


class Command(BaseCommand):
    help = 'Fetches and parses data from suppliers in YML format, updating SupplierProduct data'

    def add_arguments(self, parser):
        parser.add_argument('--supplier_id', type=int, help='ID конкретного поставщика для парсинга')

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching YML data for all active suppliers...")

        # Получаем всех активных поставщиков с поддержкой формата YML
        supplier_id = kwargs.get('supplier_id')

        if supplier_id:
            suppliers = Supplier.objects.filter(id=supplier_id, status=True, formats=Supplier.Format.YML)
        else:
            suppliers = Supplier.objects.filter(status=True, formats=Supplier.Format.YML)

        total_products = 0
        total_successful_updates = 0
        total_failed_updates = 0

        for supplier in suppliers:
            report = Report(supplier=supplier)
            report.total_products = 0
            report.successful_updates = 0
            report.failed_updates = 0
            report.failed_products = ""

            self.stdout.write(f"Processing YML supplier: {supplier.name}")

            parsing_url = XMLParsingRule.objects.filter(supplier=supplier).first()

            # Проверка на наличие scrape_url
            if not parsing_url.base_url:
                self.stderr.write(f"Supplier {supplier.name} has no scrape URL defined")
                continue

            self.process_yml_supplier(supplier, parsing_url.base_url, report)

            report.save()

            total_products += report.total_products
            total_successful_updates += report.successful_updates
            total_failed_updates += report.failed_updates

        self.stdout.write(f"Total processed items from all suppliers: {total_products}")
        self.stdout.write(f"Total successful updates: {total_successful_updates}")
        self.stdout.write(f"Total failed updates: {total_failed_updates}")

    def process_yml_supplier(self, supplier, parsing_url, report):
        self.stdout.write(f"Fetching YML data from: {parsing_url} for supplier: {supplier.name}")

        try:
            response = requests.get(parsing_url)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            # Вычисляем сигнатуру содержимого
            content_signature = hashlib.sha256(response.content).hexdigest()
            supplier_signature, created = SupplierPriceSignature.objects.get_or_create(supplier=supplier)

            # Проверка изменения сигнатуры
            if supplier_signature.signature == content_signature:
                self.stdout.write(f"No changes in supplier data for {supplier.name}. Skipping update.")
                return

            # Обновляем сигнатуру и продолжаем обработку
            supplier_signature.signature = content_signature
            supplier_signature.save()

            categories = root.find('shop/categories')

            if categories is not None:
                for category_elem in categories.findall('category'):
                    category_name = category_elem.text
                    category_id = category_elem.get('id')
                    if category_name:
                        category, created = Category.objects.get_or_create(internal_id=category_id, name=category_name)
                        supplier.categories.add(category)

            parsing_rules = XMLParsingRule.objects.filter(supplier=supplier)
            for rule in parsing_rules:
                offer_elements = root.findall(rule.element_path)

                for offer in offer_elements:
                    self.process_offer(offer, rule, supplier, report)
        except requests.exceptions.RequestException as e:
            self.stderr.write(f"Failed to fetch YML data from {supplier.name}: {e}")

    def process_offer(self, offer, rule, supplier, report):
        try:
            offer_id = offer.get('id')
            title = offer.find(rule.title_field).text
            description = offer.find(rule.description_field).text
            article = offer.find(rule.article_field).text if offer.find(rule.article_field) is not None else offer_id
            image = offer.find(rule.image_field).text
            source = offer.find(rule.link_field).text if offer.find(rule.link_field) is not NoneType else "-"
            sale_price = self.get_offer_price(offer, rule, supplier, source)
            purchase_price = self.get_offer_price(offer, rule, supplier, source)
            category = offer.find(rule.category_field).text

            if title and title.strip():
                self.update_supplier_product(rule, supplier, title, description, article, sale_price, purchase_price, image, source, category, report)
        except Exception as e:
            self.stderr.write(f"Failed to parse offer from {supplier.name}: {e}")
            report.failed_updates += 1
            report.total_products += 1

    def get_offer_price(self, offer, rule, supplier, source):
        try:
            price_text = None
            if rule.parse_price and rule.price_selector:
                price_text = parse_price_from_website(source, rule.price_selector)
                return price_text if price_text else "0"
            else:
                price_element = offer.find(rule.price_field)
                price_text = price_element.text.strip() if price_element is not None else "0"
                return PriceReplacementRule.apply_rules(supplier, price_text)
        except (AttributeError, ValueError) as e:
            self.stderr.write(f"Price parsing error: {e}")
            return "0"

    def update_supplier_product(self, rule, supplier, title, description, article, sale_price, purchase_price, image, source, category, report):
        try:
            categoryd = Category.objects.filter(internal_id=category).first()
            supplier_product, created = SupplierProduct.objects.update_or_create(
                supplier=supplier,
                name=title,
                description=description if description else "Описание отсутствует",
                article=article,
                image_url=image,
                category=categoryd,
                source_link=source,
                defaults={'sale_price': sale_price, 'purchase_price': purchase_price, 'available_stock': 0, 'last_checked': timezone.now()}
            )

            # Загрузка изображения, если товар был создан или обновлен
            if created:
                if rule.parse_image:
                    download_image_for_product.delay(article)

            report.successful_updates += 1
            report.total_products += 1

        except Exception as exception:
            self.stderr.write(f"Failed to update product {title} from supplier {supplier.name}: {exception}")
            ReportError.create_report(report, title, exception)
            report.failed_updates += 1
            report.total_products += 1
