import logging

from channels.db import database_sync_to_async
from django.utils.timezone import now
from main.utils.brom_connector import get_list_product
from main.models import IntegrateProduct
from supplier.models import Supplier

from celery import shared_task
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .utils import send_telegram_message

logger = logging.getLogger(__name__)

@shared_task
def update_or_create_products_chunk(products_data):
    """
    Эта задача обрабатывает один кусок данных и обновляет их в базе данных.
    """
    try:
        for article, data in products_data:
            IntegrateProduct.objects.update_or_create(
                article=article,
                defaults={
                    "name": data["name"],
                    "product_code": data["product_code"],
                    "description": data["description"],
                    "sale_price": data.get("retail_price", 0),
                    "purchase_price": data.get("opt_price", 0),
                    "currency": data["currency"],
                    "supplier_id": data["supplier_id"]
                }
            )
        logger.info(f"Обработан chunk с {len(products_data)} товарами.")
    except IntegrityError as e:
        logger.error(f"Ошибка целостности данных при обновлении товаров: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке chunk: {e}")
        send_telegram_message(f"Ошибка при обработке chunk: {e}")

@shared_task
def sync_products(supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)  # Получаем объект поставщика по ID
        send_telegram_message(f"Синхронизация товаров для поставщика {supplier.name} началась.")
        start_time = now()

        all_products_data = []
        list_products = get_list_product(supplier.prefix)
        if list_products:
            products_data = {}
            for row in list_products:
                article = row.Артикул
                if not article:
                    continue

                price = float(row.Цена)
                product_code = str(row.Код)
                price_type = str(row.ВидЦены)
                name = str(row.Номенклатура)
                currency = "RUB"
                description = str(row.Описание)

                if article not in products_data:
                    products_data[article] = {
                        "name": name,
                        "product_code": product_code,
                        "description": description,
                        "retail_price": None,
                        "opt_price": None,
                        "currency": currency,
                        "supplier_id": supplier.id
                    }

                if price_type == "Прайс-лист":
                    products_data[article]["retail_price"] = price
                elif price_type == "Закупочная":
                    products_data[article]["opt_price"] = price

            all_products_data.extend(products_data.items())
            logger.info(f"Added products for supplier {supplier.name}: {len(products_data)} products")

        # Now perform the database updates
        chunk_size = 100
        for i in range(0, len(all_products_data), chunk_size):
            chunk = all_products_data[i:i + chunk_size]
            update_or_create_products_chunk.delay(chunk)  # Отправляем чанки в задачу Celery

        send_telegram_message(
            f"Синхронизация товаров для поставщика {supplier.name} завершена успешно. "
            f"Обработано {len(all_products_data)} товаров за {(now() - start_time).seconds} секунд."
        )
        logger.info("Finished sending chunks to Celery.")

        logger.info("Finished updating database with integrated products.")

    except Exception as e:
        logger.error(f"Error syncing products for supplier {supplier_id}: {e}")
