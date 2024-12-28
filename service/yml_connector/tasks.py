import logging
from celery import shared_task
import requests
from django.core.files.base import ContentFile
from django.core.management import call_command
from supplier.models import Supplier

from supplier.models import SupplierProduct

logger = logging.getLogger(__name__)


@shared_task
def fetch_data_for_supplier(supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)
    call_command('parse_yml', supplier_id=supplier.id)

@shared_task
def download_image_for_product(article):
    try:
        product = SupplierProduct.objects.filter(article=article).first()

        # Загружаем изображение
        response = requests.get(product.image_url)
        if response.status_code == 200:
            # Получаем имя файла изображения
            image_name = f"{article}.jpg"

            # Сохраняем изображение в поле ImageField модели товара
            product.image.save(image_name, ContentFile(response.content), save=True)
            product.save()

            return f"Image for product {product.name} saved successfully."
        else:
            return f"Failed to download image from {product.image_url}"
    except Exception as e:
        return f"Error occurred while downloading image: {e}"