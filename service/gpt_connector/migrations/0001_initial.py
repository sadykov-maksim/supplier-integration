# Generated by Django 5.0.2 on 2024-12-10 05:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(help_text='Идентификатор пользователя', max_length=255)),
                ('message_role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant')], help_text='Роль отправителя', max_length=50)),
                ('message_content', models.TextField(help_text='Содержание сообщения')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='Время отправки сообщения')),
            ],
        ),
        migrations.CreateModel(
            name='ChatRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Дата и время создания запроса')),
                ('user_input', models.TextField(help_text='Вопрос пользователя')),
                ('model_name', models.CharField(help_text='Имя используемой модели', max_length=255)),
                ('api_key_used', models.CharField(help_text='API ключ, использованный для запроса', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GPTConnectorSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(help_text='API ключ для доступа к Mistral API', max_length=255)),
                ('model_name', models.CharField(default='mistral-large-latest', help_text='Имя модели для запросов', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Флаг активности настройки')),
            ],
        ),
        migrations.CreateModel(
            name='ChatResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_content', models.TextField(help_text='Ответ от модели')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Дата и время получения ответа')),
                ('request', models.OneToOneField(help_text='Связанный запрос', on_delete=django.db.models.deletion.CASCADE, related_name='response', to='gpt_connector.chatrequest')),
            ],
        ),
    ]
