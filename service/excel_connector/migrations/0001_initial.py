# Generated by Django 5.0.2 on 2024-12-09 06:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supplier', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelSheetParsingRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheet_name', models.CharField(help_text='Название листа Excel', max_length=100)),
                ('skip_rows', models.PositiveIntegerField(default=0, help_text='Количество строк для пропуска')),
                ('title_column', models.CharField(blank=True, help_text='Название колонки для заголовка', max_length=100, null=True)),
                ('article_column', models.CharField(blank=True, help_text='Название колонки для артикула', max_length=100, null=True)),
                ('price_column', models.CharField(blank=True, help_text='Название колонки для цены', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Правило парсинга листа',
                'verbose_name_plural': 'Правила парсинга листов',
            },
        ),
        migrations.CreateModel(
            name='ExcelFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(help_text='Загрузите файл Excel', upload_to='excel_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('supplier', models.ForeignKey(limit_choices_to={'formats': 'EXCEL'}, on_delete=django.db.models.deletion.CASCADE, related_name='excel_files', to='supplier.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='ExcelParsingSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_row', models.PositiveIntegerField(default=1)),
                ('required_columns', models.TextField(blank=True, help_text='Список обязательных столбцов, разделённых запятыми')),
                ('exclude_sheets', models.TextField(help_text='Список листов для исключения, разделённых запятыми')),
                ('excel_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parsing_settings', to='excel_connector.excelfile')),
                ('supplier', models.ForeignKey(limit_choices_to={'formats': 'EXCEL'}, on_delete=django.db.models.deletion.CASCADE, related_name='excel_parsing_rules', to='supplier.supplier')),
                ('rules', models.ManyToManyField(related_name='parsing_settings', to='excel_connector.excelsheetparsingrule')),
            ],
        ),
    ]
