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
    call_command('parse_excel', supplier_id=supplier.id)
