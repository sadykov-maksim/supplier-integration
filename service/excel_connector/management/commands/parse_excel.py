from random import random

import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from supplier.models import Supplier, SupplierProduct
from report.models import Report
from excel_connector.models import ExcelFile, ExcelParsingSettings

from report.models import ReportError

from supplier.models import Category

from yml_connector.models import PriceReplacementRule


class Command(BaseCommand):
    help = 'Parses data from uploaded Excel files, updating SupplierProduct data'

    def add_arguments(self, parser):
        parser.add_argument('--supplier_id', type=int, help='ID конкретного поставщика для парсинга')

    def handle(self, *args, **kwargs):
        self.stdout.write("Parsing data for all active suppliers with Excel files...")

        # Получаем всех активных поставщиков с поддержкой формата YML
        supplier_id = kwargs.get('supplier_id')

        if supplier_id:
            suppliers = Supplier.objects.filter(id=supplier_id, status=True, formats=Supplier.Format.EXCEL)
        else:
            suppliers = Supplier.objects.filter(status=True, formats=Supplier.Format.EXCEL)

        for supplier in suppliers:
            # Получаем все активные файлы Excel для поставщиков, которые поддерживают формат EXCEL
            excel_files = ExcelFile.objects.filter(supplier_id=supplier.id, supplier__formats=Supplier.Format.EXCEL)

            total_products = 0
            total_successful_updates = 0
            total_failed_updates = 0

            for excel_file in excel_files:
                supplier = excel_file.supplier
                report = Report(supplier=supplier)
                report.total_products = 0
                report.successful_updates = 0
                report.failed_updates = 0
                report.failed_products = ""
                self.stdout.write(f"Загружен файл: {excel_file.file}")
                self.stdout.write(f"Processing Excel file for supplier: {supplier.name}")
                self.process_excel_file(excel_file, report)
                report.save()

                total_products += report.total_products
                total_successful_updates += report.successful_updates
                total_failed_updates += report.failed_updates

            self.stdout.write(f"Total processed items from all suppliers: {total_products}")
            self.stdout.write(f"Total successful updates: {total_successful_updates}")
            self.stdout.write(f"Total failed updates: {total_failed_updates}")

    def process_excel_file(self, excel_file, report):
        # Получаем настройки парсинга для текущего файла и поставщика
        parsing_settings = ExcelParsingSettings.objects.filter(supplier=excel_file.supplier).first()
        if not parsing_settings:
            self.stderr.write(f"No parsing settings found for supplier {excel_file.supplier.name}")
            return


        allowed_sheets = parsing_settings.rules.values_list('sheet_name', flat=True)

        try:
            for sheet_name in pd.ExcelFile(excel_file.file.path).sheet_names:
                if sheet_name not in allowed_sheets:
                    self.stdout.write(f"Skipping sheet {sheet_name} (excluded)")
                    continue

                # Создание списка категорий
                if sheet_name:
                    category, created = Category.objects.get_or_create(internal_id=0, name=sheet_name)
                    excel_file.supplier.categories.add(category)

                # Применяем правила для текущего листа
                rule = parsing_settings.rules.filter(sheet_name=sheet_name).first()
                skip_rows = rule.skip_rows if rule else 0

                sheet_data = pd.read_excel(
                    excel_file.file.path,
                    sheet_name=sheet_name,
                    skiprows=skip_rows
                )

                # Парсим данные на основе колонок
                self.parse_excel_sheet(sheet_data, sheet_name, rule, excel_file.supplier, report)

        except Exception as e:
            self.stderr.write(f"Failed to process Excel file for supplier {excel_file.supplier.name}: {e}")

    def parse_excel_sheet(self, sheet_data, sheet_name, rule, supplier, report):
        previous_row = None  # Переменная для хранения предыдущей строки

        for index, row in sheet_data.iterrows():

            title = row.get(rule.title_column) if rule.title_column else None
            article = row.get(rule.article_column) if rule.article_column else None
            price = row.get(rule.price_column) if rule.price_column else 0
            description = row.get(rule.description_column) if rule.description_column else "-"
            image = row.get(rule.image_column) if rule.image_column else ""



            # Сохраняем текущую строку для использования в следующей итерации
            previous_row = row

            if pd.notna(article) and pd.notna(price):
                try:
                    # Если предыдущая строка существует, возвращаем нужные данные из неё
                    if previous_row is not None:
                        title = previous_row.get(rule.title_column) if rule.title_column else None
                        self.stderr.write(f"Previous title: {title}, article: {article}, price: {price}")
                    self.update_supplier_product(sheet_name, supplier, title, article, description, price, report)
                except Exception as e:
                    self.stderr.write(f"Failed to update product {title} for supplier {supplier.name}: {e}")
                    report.failed_updates += 1
                    report.total_products += 1

    def update_supplier_product(self, sheet_name, supplier, title, article, description, price, report):
        try:
            # Ищем категорию по названию
            category = Category.objects.filter(name=sheet_name).first()

            supplier_product, created = SupplierProduct.objects.update_or_create(
                supplier=supplier,
                name=title,
                description=description,
                category=category,
                article=article,
                defaults={'sale_price': price, 'purchase_price': price, 'available_stock': 0,
                          'last_checked': timezone.now()}
            )
            report.successful_updates += 1
            report.total_products += 1

        except Exception as exception:
            self.stderr.write(f"Failed to update product {title} from supplier {supplier.name}: {exception}")
            ReportError.create_report(report, title, exception)
            report.failed_updates += 1
            report.total_products += 1
