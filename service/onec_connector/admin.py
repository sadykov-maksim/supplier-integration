import logging

from django.urls import path
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

from .management.commands.onec_client import create_client
from .models import *
from .tasks import check_connections

# Register your models here.
@admin.register(OneCConfiguration)
class OneCConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'description')
    list_filter = ('active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {"description": ("name",)}
    ordering = ('name',)


# Настройка отображения подключений 1С
@admin.register(OneCConnection)
class OneCConnectionAdmin(admin.ModelAdmin):
    list_display = ('config', 'url', 'database', 'username', 'created_at')
    list_filter = ('config', 'created_at')
    search_fields = ('url', 'database', 'username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    actions = ['check_connection', ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('password',)
        return self.readonly_fields

    @admin.action(description='Проверить подключение')
    def check_connection(self, request, queryset):
        for connection in queryset:
            # Try connecting
            try:
                client = create_client(
                    url=connection.url,
                    database=connection.database,
                    username=connection.username,
                    password=connection.password,
                )
                self.message_user(request, f"Successfully connected to {connection.url}/{connection.database}", level=logging.INFO)
            except Exception as e:
                self.message_user(request, f"Connection error for {connection.url}: {e}", level=logging.ERROR)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))






