from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)