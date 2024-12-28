import decimal

from django.db import models

from supplier.models import Supplier


# Create your models here.
class PriceReplacementRule(models.Model):
    """Модель для хранения правил замены строк для обработки цен"""

    find_str = models.CharField(max_length=255, verbose_name="Искомая строка")
    replace_str = models.CharField(max_length=255, verbose_name="Строка замены", null=True, blank=True)

    class Meta:
        verbose_name = "Правило замены цены"
        verbose_name_plural = "Правила замены цен"

    def __str__(self):
        return f"Заменить '{self.find_str}' на '{self.replace_str}'"

    @classmethod
    def apply_rules(cls, supplier, price_text):
        """Применяет все правила замены к строке с ценой"""
        rules = XMLParsingRule.objects.filter(supplier=supplier).first()
        if rules:
            # Получаем все связанные правила для замены
            price_rules = rules.price_replace.all()
            for rule in price_rules:
                price_text = price_text.replace(rule.find_str, rule.replace_str)
            try:
                return decimal.Decimal(price_text)
            except ValueError:
                raise ValueError("Цена не может быть преобразована в число.")
        else:
            return 0.0


class XMLParsingRule(models.Model):
    """Parsing Rules for XML Format"""

    supplier = models.ForeignKey(
        Supplier,
        limit_choices_to={"formats": "YML"},
        on_delete=models.CASCADE,
        related_name="xml_parsing_rules"
    )
    base_url = models.URLField(verbose_name="Базовый URL XML", help_text="Базовый URL XML")
    element_path = models.CharField(max_length=255, default="shop/offers/offer" ,help_text="XPath путь к элементу предложения")
    title_field = models.CharField(max_length=255, default="name", help_text="Название тега для заголовка товара")
    description_field = models.CharField(max_length=255, default="description")
    article_field = models.CharField(max_length=255, default="article" ,help_text="Название тега для артикула")
    price_field = models.CharField(max_length=255, default="price" ,help_text="Название тега для цены")
    image_field = models.CharField(max_length=255, default="picture", help_text="Название тега для изображения", null=True, blank=True)
    category_field = models.CharField(max_length=255, default="categoryId", help_text="Название тега для категории", null=True, blank=True)
    link_field = models.CharField(max_length=255, default="url", help_text="Название тега для ссылки", null=True, blank=True)
    price_replace = models.ManyToManyField(PriceReplacementRule, related_name="products", blank=True)

    parse_price = models.BooleanField(
        default=False,
        verbose_name="Парсить цену с сайта",
        help_text="Указывает, нужно ли парсить цену напрямую с сайта"
    )
    price_selector = models.CharField(max_length=255, help_text="CSS-селектор или XPath для цены", null=True, blank=True)

    parse_image = models.BooleanField(
        default=False,
        verbose_name="Парсить изображение с сайта",
        help_text="Указывает, нужно ли парсить изображение напрямую с сайта"
    )

    def __str__(self):
        return f"XML Parsing Rule for {self.supplier.name}"

