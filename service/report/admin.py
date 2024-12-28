from django.contrib import admin
from report.models import *

# Register your models here.
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'created_at', 'successful_updates', 'failed_updates', 'total_products')
    search_fields = ('supplier__name',)
    list_filter = ('supplier', 'created_at')
    readonly_fields = ('created_at', )

    def add_failed_product(self, request, queryset):
        for report in queryset:
            report.add_failed_product('Example Product')
            report.save()

    actions = ['add_failed_product']

@admin.register(ReportError)
class ReportErrorAdmin(admin.ModelAdmin):
    pass