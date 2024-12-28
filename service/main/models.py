from django.db import models
from django.utils import timezone
from supplier.models import Supplier


# Create your models here.
class IntegrateProduct(models.Model):
    """Product Information Available on the Site"""
    name = models.CharField(max_length=100)
    product_code = models.CharField(max_length=100, verbose_name="Product Code")
    description = models.TextField(default="", verbose_name="Описание")
    neuro_description = models.TextField(default="", verbose_name="нейро-описание")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    image = models.ImageField(default='products/placeholder.png', upload_to='products', null=True, blank=True)
    sale_price = models.FloatField()
    article = models.CharField(max_length=100, null=True, blank=True)
    purchase_price = models.FloatField()
    currency = models.CharField(max_length=30, default='RUB')
    last_updated = models.DateTimeField(default=timezone.now)

    #def save(self, *args, **kwargs):
    #    if self.image:
    ##        watermark = Watermark.objects.filter(is_active=True).first()
    ##        if watermark:
    ##            watermarked_image = add_image_watermark(self.image, watermark)
    ##            self.image.save(self.image.name, watermarked_image, save=False)
#
     #   super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductMatchRule(models.Model):
    """Модель для сопоставлений товаров по началу артикула"""

    prefix = models.CharField(max_length=50)  # Префикс артикула для поиска
    supplier_prefix = models.CharField(max_length=50, null=True, blank=True)  # Префикс артикула у поставщика

    def __str__(self):
        return f"Правило: {self.prefix} -> {self.supplier_prefix}"

    @staticmethod
    def find_matched_supplier_article(article):
        """Метод для поиска соответствующего артикула у поставщика по префиксу"""
        for rule in ProductMatchRule.objects.all():
            if article.startswith(rule.prefix):
                return article.replace(rule.prefix, rule.supplier_prefix, 1)
        return article

