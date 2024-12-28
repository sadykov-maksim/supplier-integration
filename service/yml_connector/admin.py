from django.contrib import admin
from .models import *
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse

from django.contrib import messages
from django.urls import path

from .tasks import fetch_data_for_supplier
from supplier.models import Supplier


# Register your models here.
@admin.register(XMLParsingRule)
class XMLParsingRuleAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'element_path', 'title_field', 'article_field', 'price_field')
    search_fields = ('element_path',)
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




@admin.register(PriceReplacementRule)
class PriceReplacementRuleAdmin(admin.ModelAdmin):
    list_display = ('find_str', 'replace_str')
    search_fields = ('find_str', 'replace_str')