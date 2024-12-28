from django.contrib import admin
from .models import *
from django.contrib import messages

from supplier.models import Supplier
from .tasks import fetch_data_for_supplier


# Register your models here.
@admin.register(ExcelSheetParsingRule)
class ExcelSheetParsingRuleAdmin(admin.ModelAdmin):
    list_display = ('sheet_name', 'skip_rows', 'title_column', 'article_column', 'price_column',)
    search_fields = ('sheet_name',)



@admin.register(ExcelParsingSettings)
class ExcelParsingSettingsAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'start_row', )
    search_fields = ('supplier__name',)
    list_filter = ('supplier',)
    actions = ['parse',]

    @admin.action(description="Анализ XML для выбранных поставщиков")
    def parse(self, request, queryset):
        selected_suppliers = queryset.values_list('supplier', flat=True).distinct()

        if not selected_suppliers:
            messages.error(request, "Не выбраны правила для обработки.")
            return

        # Получаем названия поставщиков
        suppliers = Supplier.objects.filter(id__in=selected_suppliers)

        # Запуск Celery-задачи для выбранных поставщиков
        for supplier in suppliers:
            fetch_data_for_supplier.delay(supplier.id)
            messages.info(request, f"Запущена обработка для поставщика: {supplier.name}")

        messages.success(request, "Обработка выбранных правил начата.")


@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'uploaded_at')
    search_fields = ('supplier__name',)