from django.contrib import admin
from .models import *
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse

from yml_connector.tasks import download_image_for_product
from django.utils.safestring import mark_safe
from .tasks import sync_products
from .utils import send_telegram_message


# Register your models here.

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'prefix', 'formats', 'created_at', 'updated_at', 'status')
    search_fields = ('name', 'prefix')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['get_products']

    @admin.action(description='Получить товары из 1С')
    def get_products(self, request, queryset):
        # Получаем ID поставщика, для которого нужно выполнить задачу
        for supplier in queryset:
            send_telegram_message(f"Синхронизация товаров для поставщика {supplier.name} начата.")
            sync_products.delay(supplier.id)  # Передаем ID поставщика в задачу Celery

        self.message_user(request, "Задача синхронизации товаров запущена.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@admin.register(SupplierPriceSignature)
class SupplierPriceSignatureAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'signature', 'updated_at')
    search_fields = ('supplier__name',)
    readonly_fields = ('signature', 'updated_at')
    list_filter = ('updated_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('supplier')


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'name', 'supplier', 'article', 'sale_price', 'purchase_price', 'available_stock', 'source_link', 'last_checked')
    search_fields = ('name', 'article')
    list_filter = ('supplier',)
    readonly_fields = ('last_checked','preview')
    list_display_links = ('name',)
    actions=['download_images_for_selected', ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'supplier', 'article', 'description', 'category', 'source_link')
        }),
        ('Данные изображения', {
            'fields': ('preview', 'image')
        }),
        ('Финансовая информация', {
            'fields': ('sale_price', 'purchase_price', 'available_stock')
        }),
        ('Дополнительная информация', {
            'fields': ('last_checked',),
        }),
    )

    @admin.action(description="Загрузить изображения для выбранных товаров")
    def download_images_for_selected(self, request, queryset):
        for product in queryset:
            # Вызов Celery задачи для каждого товара
            download_image_for_product.delay(product.article)
            self.message_user(request, f"Загрузка изображения для товара {product.name} начата.", level=messages.INFO)

        self.message_user(request, "Загрузка изображений начата для выбранных товаров.", level=messages.INFO)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @admin.action(description='Получить изображения')
    def get_images(self, request, queryset):
        #for product in queryset:
        #    download_image_for_product.delay(product.article)
        self.message_user(request, "Создано нейро-описание для товара!")

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-width:275px; max-height:275px"/>')

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" alt="image" class="thumbnail-image" style="max-width: 75px; max-height: 75px;" data-toggle="modal" data-target="#imageModal" data-image="{obj.image.url}"  data-title="{obj.name}"  data-article="{obj.article}"  data-price="{obj.sale_price}"  data-description="{"obj.description"}"/>')
        else:
            return mark_safe(
                f'<img src="https://placehold.co/500x500/png?text=Не+найдено" style="max-width:75px; max-height:75px" class="thumbnail-image" />')

    preview.allow_tags = True
    preview.short_description = 'Предварительный просмотр'

