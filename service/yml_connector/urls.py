from .views import sync_products
from django.urls import path

urlpatterns = [
    path('sync_products/', sync_products, name='sync_products'),
]
