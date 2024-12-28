import requests
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from django.utils import timezone
from supplier.models import Supplier


def handle(self, *args, **kwargs):
    self.stdout.write("Fetching data for all suppliers...")

    # Получаем всех поставщиков с форматом взаимодействия
    suppliers = Supplier.objects.all()

    # Создаем общий отчет
    total_products = 0
    total_successful_updates = 0
    total_failed_updates = 0

    for supplier in suppliers:
        report = Report(supplier=supplier)
        report.total_products = 0
        report.successful_updates = 0
        report.failed_updates = 0
        report.failed_products = ""

        interaction_formats = Supplier.objects.filter(supplier=supplier)

        for interaction_format in interaction_formats:
            self.stdout.write(f"Processing supplier: {supplier.name} with format: {interaction_format.name}")

            if interaction_format.formats.name == "API":
                print(supplier.name)
                self.process_api_supplier(supplier, interaction_format, report)
            elif interaction_format.format.name == "YML":
                self.process_yml_supplier(supplier, interaction_format, report)

        report.save()

        # Добавляем в общий подсчет
        total_products += report.total_products
        total_successful_updates += report.successful_updates
        total_failed_updates += report.failed_updates

    self.stdout.write(f"Total processed items from all suppliers: {total_products}")
    self.stdout.write(f"Total successful updates: {total_successful_updates}")
    self.stdout.write(f"Total failed updates: {total_failed_updates}")

def process_api_supplier(self, supplier, interaction_format, report):
    api_url = supplier.api_endpoint

    if not api_url:
        self.stderr.write(f"No API endpoint found for supplier {supplier.name}")
        return

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'content-type': 'application/json; charset=utf-8',
        'origin': 'https://examen-technolab.ru',
        'priority': 'u=1, i',
        'referer': 'https://examen-technolab.ru/',
        'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(response)
        self.stdout.write(f"Successfully fetched data from {supplier.name}")
        for item in data:
            self.process_api_item(item, headers, supplier, report)
    except requests.exceptions.RequestException as e:
        self.stderr.write(f"Failed to fetch data from {supplier.name}: {e}")

def process_api_item(self, item, headers, supplier, report):
    card_id = item.get('id')
    if card_id:
        card_detail_url = f"https://api.examen-technolab.ru/card?id={card_id}"
        try:
            print(card_detail_url)
            card_response = requests.get(card_detail_url, headers=headers, timeout=10)
            card_response.raise_for_status()
            card_details = card_response.json()

            for card_detail in card_details:
                card_title = card_detail.get('title')
                card_price = card_detail.get('price').replace(' ', '') if card_detail.get('price') else 0
                card_article = card_detail.get('article')

                product, created = Product.objects.get_or_create(
                    name=card_title,
                    article=card_article,
                    defaults={'sale_price': card_price, 'purchase_price': card_price}
                )

                supplier_product, created = SupplierProduct.objects.update_or_create(
                    supplier=supplier,
                    product=product,
                    article=card_article,
                    defaults={'supplier_price': card_price, 'available_stock': 0, 'last_checked': timezone.now()}
                )

                report.successful_updates += 1
                report.total_products += 1
        except Exception as e:
            self.stderr.write(f"Failed to update product from API for supplier {supplier.name}: {e}")
            report.failed_updates += 1
            report.total_products += 1

def process_yml_supplier(self, supplier, interaction_format, report):
    url = interaction_format.source
    self.stdout.write(f"Fetching YML data from: {url} for supplier: {supplier.name}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        parsing_rules = XMLParsingRule.objects.filter(format=interaction_format)

        for rule in parsing_rules:
            offer_elements = root.findall(rule.element_path)

            for offer in offer_elements:
                self.process_offer(offer, rule, supplier, report)
    except requests.exceptions.RequestException as e:
        self.stderr.write(f"Failed to fetch YML data from {supplier.name}: {e}")

def process_offer(self, offer, rule, supplier, report):
    try:
        title = offer.find(rule.title_field).text
        article = offer.find(rule.article_field).text if offer.find(rule.article_field) is not None else "-"
        price = float(offer.find(rule.price_field).text) if offer.find(rule.price_field) is not None else 0

        if title and title.strip() != '':
            self.update_supplier_product(supplier, title, article, price, report)
    except Exception as e:
        self.stderr.write(f"Failed to parse offer from {supplier.name}: {e}")
        report.failed_updates += 1
        report.total_products += 1

def update_supplier_product(self, supplier, title, article, price, report):
    try:
        product, created = Product.objects.get_or_create(
            name=title,
            article=article,
            defaults={'sale_price': price, 'purchase_price': price}
        )

        supplier_product, created = SupplierProduct.objects.update_or_create(
            supplier=supplier,
            product=product,
            article=article,
            defaults={'supplier_price': price, 'available_stock': 0, 'last_checked': timezone.now()}
        )

        report.successful_updates += 1
        report.total_products += 1

    except Exception as e:
        self.stderr.write(f"Failed to update product {title} from {supplier.name}: {e}")
        report.failed_updates += 1
        report.total_products += 1
