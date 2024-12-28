import logging

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.safestring import mark_safe

from main.models import IntegrateProduct, ProductMatchRule
from main.utils.brom_connector import read_from_csv, create_client, get_supplier_by_sku, get_list_product
from supplier.models import Supplier, SupplierProduct

from gpt_connector.utils.get_chat_response import get_chat_response

from .tasks import generate_neuro_description, update_description, save_to_csv_task


# Register your models here.



@admin.register(IntegrateProduct)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_tag','name', "neuro_description", 'article',  'supplier', 'sale_price', 'purchase_price', 'last_updated',)
    search_fields = ('name', 'article')
    list_filter = ('last_updated', 'supplier',)
    readonly_fields = ('last_updated', 'preview')
    list_display_links = ('name', 'image_tag')
    actions=['sync_and_add_products', 'sync_products','neuro_description', 'get_products', 'update_description_product_1c', ]


    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-width:275px; max-height:275px"/>')
    preview.allow_tags = True
    preview.short_description = 'Предварительный просмотр'

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-width:75px; max-height:75px"/>')

    fieldsets = [
        (
            "Basic",
            {
                "fields": ["article", "product_code", "name", "description",  "supplier", "preview", "image", "sale_price", "purchase_price", "last_updated"],
                "classes": ["wide"],

            },
        ),
        (
            "Neuro",
            {
                "fields": [ "neuro_description", ],
                "classes": ["collapse"],

            }
        )
    ]
    @admin.action(description='SYNC')
    def sync_products(self, request, queryset):
        # Ваш произвольный код для синхронизации
        client = create_client()

        if client:
            suppliers = Supplier.objects.all()
            print(f"Обрабатываем {len(suppliers)} поставщиков.")
            for supplier in suppliers:
                print(f"Обработка поставщика: {supplier.name}")
                list_products = read_from_csv(
                    f"{supplier.prefix}.csv")
                if list_products:
                    print(f"Найдено {len(list_products)} товаров для поставщика {supplier.name}.")
                    products_data = {}

                    for row in list_products:
                        article = row.get('Артикул')
                        if not article:
                            print(f"Артикул отсутствует в данных для поставщика {supplier.name}!")
                            continue

                        supplier_from_article = get_supplier_by_sku(article)  # Ищем поставщика по артикулу
                        if supplier_from_article:
                            print(f"Найден поставщик для артикул: {article} - {supplier_from_article.name}")
                        else:
                            print(f"Поставщик с артикулом {article} не найден для {supplier.name}.")
                            continue  # Пропускаем товар, если поставщик не найден

                        price = row.get('Цена')  # Получаем цену товара
                        price_type = row.get('ВидЦены')  # Тип цены
                        name = row.get('Номенклатура')  # Наименование товара
                        currency = row.get('Валюта', "RUB")  # Валюта, по умолчанию RUB
                        description = row.get('Описание')  # Описание товара

                        # Добавляем товар в словарь, если его ещё нет
                        if article not in products_data:
                            products_data[article] = {
                                "name": name,
                                "code": article,
                                "description": description,
                                "retail_price": None,
                                "opt_price": None,
                                "валюта": currency,
                                "supplier_id": supplier.id  # Используем id поставщика из массива поставщиков
                            }

                        # Заполнение цен в зависимости от типа цены
                        if price_type == "Прайс-лист":
                            products_data[article]["retail_price"] = price
                        elif price_type == "Закупочная":
                            products_data[article]["opt_price"] = price

                    # Обновление или создание записи в базе данных для каждого товара
                    for article, data in products_data.items():
                        IntegrateProduct.objects.update_or_create(
                            article=article,  # Поле для идентификации существующих записей
                            defaults={
                                "name": data["name"],
                                "product_code": data["code"],
                                "description": data["description"],
                                "sale_price": data["opt_price"] if data["opt_price"] is not None else 0,
                                "purchase_price": data["retail_price"] if data["retail_price"] is not None else 0,
                                "currency": data["валюта"],
                                "supplier_id": data["supplier_id"]
                            }
                        )

                    self.message_user(request,
                                      f"Товары для поставщика {supplier.name} успешно добавлены и синхронизированы!")
                else:
                    print(f"Файл CSV для поставщика {supplier.name} пустой или не найден.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



    @admin.action(description='Сравнить цены с прайсами')
    def sync_and_add_products(self, request, queryset):
        for product in queryset:
            supplier_prefix = product.supplier.prefix
            clean_article = None

            if product.article.startswith(supplier_prefix):
                clean_article = product.article[len(supplier_prefix):].lstrip('-')

            matching_products = SupplierProduct.objects.filter(article=clean_article)

            if matching_products.exists():
                for match in matching_products:

                    logging.info(f"Товар с артикулом {product.article} найден в базе: {match.article}, старая цена: {match.sale_price}")

                    product.sale_price  = match.sale_price # Обновление цены
                    #product.image  = match.image # Обновление цены
                    #print(match.image)
                    product.save()
                    #client = create_client()
                    #update_product(client, match.article, "Retail")

                    # Логируем, что цены обновлены
                    #logging.info(f"Цены для товара (артикул {match.article}) обновлены на новые значения: {match.sale_price}")

                    self.message_user(request, f"Товар с артикулом {product.article} найден в базе: {match.article}, старая цена: {match.sale_price}")
            else:
                # Логируем, если совпадений нет
                self.message_user(request, f"Совпадений для товара с артикулом {product.article} не найдено.", level=messages.ERROR)
                logging.info(f"Совпадений для товара с артикулом {product.article} не найдено.")


        self.message_user(request, "Товары успешно синхронизированы и добавлены!")

    @admin.action(description='Обновить цену на товары в 1с')
    def get_products(self, request, queryset):
        for product in queryset:
            prices = {
                "Закупочная": product.purchase_price,
                "Прайс-лист": product.sale_price,
            }
            client = create_client()

            for price_type, price_value in prices.items():
                new_price = client.Справочники.Справочник1.УстановитьЦенуНоменклатуры(
                    product.product_code, price_value, price_type
                )
        self.message_user(request, "Задача синхронизации товаров запущена.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    @admin.action(description='Создать нейро-описание')
    def neuro_description(self, request, queryset):
        for product in queryset:
            content = (f"Создайте подробное описание карточки товара на русском языке, используя HTML для оформления. Описание должно включать ключевые особенности, преимущества и другие важные детали, которые могут заинтересовать покупателей. Ответ должен содержать только текст описания, оформленный с помощью HTML-тегов (например, <p>, <ul>, <li>, <strong>, и т. д.)."
                       f"Название товара: {product.name})"
                       f"Описание товара: {product.description}")
            generate_neuro_description.delay(product.id, content)  # Асинхронный вызов задачи
        self.message_user(request, "Задачи на создание нейро-описаний добавлены в очередь!")

    @admin.action(description='Обновить описание товаров 1С')
    def update_description_product_1c(self, request, queryset):
        for product in queryset:
            update_description.delay(product.id)  # Асинхронный вызов задачи
        self.message_user(request, "Задачи на создание нейро-описаний добавлены в очередь!")