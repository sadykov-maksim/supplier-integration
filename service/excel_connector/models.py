from django.db import models

from supplier.models import Supplier


# Create your models here.
class ExcelFile(models.Model):
    """Model to store uploaded Excel files for parsing."""

    file = models.FileField(upload_to='excel_files/', help_text="Загрузите файл Excel")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(
        Supplier,
        limit_choices_to={"formats": "EXCEL"},  # Ограничиваем выбор поставщиков только теми, у кого формат YML
        on_delete=models.CASCADE,
        related_name="excel_files"
    )

    def __str__(self):
        return f"Excel File for {self.supplier.name} uploaded on {self.uploaded_at}"


class ExcelSheetParsingRule(models.Model):
    """Rules for Parsing Excel Sheets"""

    sheet_name = models.CharField(max_length=100, help_text="Название листа Excel")
    skip_rows = models.PositiveIntegerField(default=0, help_text="Количество строк для пропуска")
    title_column = models.CharField(max_length=100, help_text="Название колонки для заголовка", null=True, blank=True)
    article_column = models.CharField(max_length=100, help_text="Название колонки для артикула", null=True, blank=True)
    price_column = models.CharField(max_length=100, help_text="Название колонки для цены", null=True, blank=True)
    description_column = models.CharField(max_length=100, help_text="Название колонки для описания", null=True, blank=True)
    image_column = models.CharField(max_length=100, help_text="Название колонки для изображения", null=True, blank=True)


    def __str__(self):
        return f"Правила для листа {self.sheet_name} "

    class Meta:
        verbose_name = "Правило парсинга листа"
        verbose_name_plural = "Правила парсинга листов"


class ExcelParsingSettings(models.Model):
    """Settings for Excel Parsing"""

    supplier = models.ForeignKey(
        Supplier,
        limit_choices_to={"formats": "EXCEL"},  # Ограничиваем выбор поставщиков только теми, у кого формат YML
        on_delete=models.CASCADE,
        related_name="excel_parsing_rules"
    )
    rules = models.ManyToManyField(ExcelSheetParsingRule, related_name="parsing_settings")
    start_row = models.PositiveIntegerField(default=1)
    excel_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE, null=True, blank=True, related_name='parsing_settings')

    def __str__(self):
        return f"Настройки парсинга для {self.supplier.name} (начальная строка: {self.start_row})"

