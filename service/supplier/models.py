from django.db import models
from django.utils import timezone
from django.core.validators import MaxLengthValidator, MinValueValidator, RegexValidator



# Create your models here.
class Category(models.Model):
    """Category model to store categories for suppliers."""
    name = models.CharField(max_length=255)
    internal_id = models.IntegerField(default=0, verbose_name="Internal ID")

    def __str__(self):
        return self.name

class Supplier(models.Model):
    """Supplier Information"""

    class Format(models.TextChoices):
        API = "API", ("API")
        EXCEL = "EXCEL", ("EXCEL")
        CSV = "CSV", ("CSV")
        YML = "YML", ("YML")
        SCRAPY = "SCRAPY", ("SCRAPY")
        EMPTY = "EMPTY", ("-")

    name = models.CharField(max_length=100)
    prefix = models.TextField(max_length=50)
    formats = models.CharField(max_length=6,
        choices=Format,
        default=Format.EMPTY, verbose_name="Форматы взаимодействия")
    categories = models.ManyToManyField(Category, blank=True)

    status = models.BooleanField(default=False, verbose_name="Статус")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SupplierPriceSignature(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name='price_signature')
    signature = models.CharField(max_length=64)
    updated_at = models.DateTimeField(auto_now=True)


class SupplierProduct(models.Model):
    """Product Details from a Supplier"""

    name = models.CharField(max_length=256, validators=[MaxLengthValidator(256)], verbose_name="Название товара")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products", verbose_name="Поставщик")
    article = models.CharField(max_length=100, null=True, blank=True, verbose_name="Артикул")
    description = models.TextField(default="Описание отсутствует", null=True, blank=True, verbose_name="Описание товара")
    image_url = models.CharField(max_length=256, null=True, blank=True, verbose_name="Ссылка на изображение")
    image = models.ImageField(default='products/placeholder.png', upload_to='products/', max_length=256, null=True, blank=True, verbose_name="Изображение товара")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Цена продажи")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Цена закупки")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="products", verbose_name="Категория")
    source_link = models.SlugField(null=True, blank=True, max_length=256, verbose_name="Ссылка на источник")
    available_stock = models.PositiveIntegerField(validators=[MinValueValidator(0)], verbose_name="Доступное количество")
    last_checked = models.DateTimeField(default=timezone.now, verbose_name="Дата последней проверки")

    class Meta:
        verbose_name = "Товары поставщика"
        verbose_name_plural = "Товары поставщиков"
        ordering = ['-last_checked']
        db_table = 'supplier_product'

    def __str__(self):
        return f"{self.name} from {self.supplier.name}"
