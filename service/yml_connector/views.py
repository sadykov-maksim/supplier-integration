from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.contrib import messages


# Create your views here.
def sync_products(request):
    # Логика для синхронизации товаров
    # Например, создание или обновление товаров
    #new_product = IntegrateProduct.objects.create(
    #    name="Автоматически добавленный товар",
    #    article="AUTO001",
    #    sale_price=1000,
    #    purchase_price=700
    #)

    messages.success(request, "Товары успешно синхронизированы и добавлены!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
