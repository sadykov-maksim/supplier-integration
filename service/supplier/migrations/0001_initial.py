# Generated by Django 5.0.2 on 2024-12-09 06:02

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('internal_id', models.IntegerField(default=0, verbose_name='Internal ID')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('prefix', models.TextField(max_length=50)),
                ('formats', models.CharField(choices=[('API', 'API'), ('EXCEL', 'EXCEL'), ('CSV', 'CSV'), ('YML', 'YML'), ('SCRAPY', 'SCRAPY'), ('EMPTY', '-')], default='EMPTY', max_length=6, verbose_name='Форматы взаимодействия')),
                ('status', models.BooleanField(default=False, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categories', models.ManyToManyField(blank=True, to='supplier.category')),
            ],
        ),
        migrations.CreateModel(
            name='SupplierPriceSignature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature', models.CharField(max_length=64)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('supplier', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='price_signature', to='supplier.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='SupplierProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, validators=[django.core.validators.MaxLengthValidator(256)], verbose_name='Название товара')),
                ('article', models.CharField(blank=True, max_length=100, null=True, verbose_name='Артикул')),
                ('description', models.TextField(blank=True, default='Описание отсутствует', null=True, verbose_name='Описание товара')),
                ('image_url', models.CharField(blank=True, max_length=256, null=True, verbose_name='Ссылка на изображение')),
                ('image', models.ImageField(blank=True, default='products/placeholder.png', max_length=256, null=True, upload_to='products/', verbose_name='Изображение товара')),
                ('sale_price', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена продажи')),
                ('purchase_price', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена закупки')),
                ('source_link', models.SlugField(blank=True, max_length=256, null=True, verbose_name='Ссылка на источник')),
                ('available_stock', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Доступное количество')),
                ('last_checked', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата последней проверки')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='supplier.category', verbose_name='Категория')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='supplier.supplier', verbose_name='Поставщик')),
            ],
            options={
                'verbose_name': 'Товары поставщика',
                'verbose_name_plural': 'Товары поставщиков',
                'db_table': 'supplier_product',
                'ordering': ['-last_checked'],
            },
        ),
    ]
