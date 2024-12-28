# Generated by Django 5.0.2 on 2024-12-10 05:39

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supplier', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductMatchRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(max_length=50)),
                ('supplier_prefix', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IntegrateProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default='', verbose_name='Описание')),
                ('neuro_description', models.TextField(default='', verbose_name='нейро-описание')),
                ('image', models.ImageField(blank=True, default='products/placeholder.png', null=True, upload_to='products')),
                ('sale_price', models.FloatField()),
                ('article', models.CharField(blank=True, max_length=100, null=True)),
                ('purchase_price', models.FloatField()),
                ('currency', models.CharField(default='RUB', max_length=30)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplier.supplier')),
            ],
        ),
    ]