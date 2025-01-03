# Generated by Django 5.0.2 on 2024-12-18 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Default Bot', max_length=255)),
                ('token', models.CharField(help_text='Telegram Bot Token', max_length=255)),
                ('chat_id', models.CharField(help_text='Chat ID для отправки уведомлений', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Включить отправку уведомлений')),
            ],
        ),
    ]
