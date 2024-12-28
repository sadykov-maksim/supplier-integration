from celery import shared_task
from main.models import IntegrateProduct
from gpt_connector.utils.get_chat_response import get_chat_response  # Подключите свою функцию обновления описания
from .utils.brom_connector import update_product_description, save_to_csv


@shared_task
def generate_neuro_description(product_id, content):
    product = IntegrateProduct.objects.get(id=product_id)
    product.neuro_description = get_chat_response(content)
    product.save()

@shared_task
def update_description(product_id):
    product = IntegrateProduct.objects.get(id=product_id)
    update_product_description(product.article, product.neuro_description)

@shared_task
def save_to_csv_task(data, filename):
    """Фоновая задача для сохранения данных в CSV."""

    try:
        save_to_csv(data, filename)
    except Exception as error:
        print(f"Ошибка при сохранении в CSV: {error}")