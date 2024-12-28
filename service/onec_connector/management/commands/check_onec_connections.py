import logging

from django.core.management.base import BaseCommand
from django.http import HttpResponseRedirect
from onec_connector.models import OneCConnection
from .onec_client import create_client  # Импорт вашей функции создания клиента

class Command(BaseCommand):
    help = 'Check connections to 1C configurations'

    def handle(self, request, *args, **kwargs):
        connections = OneCConnection.objects.all()  # Получаем все подключения

        for connection in connections:
            self.message_user(request, f"Проверка подключения: {connection.url}/{connection.database}", level=logging.INFO)

            # Проверка соединения
            try:
                client = create_client(
                    url=connection.url,
                    database=connection.database,
                    username=connection.username,
                    password=connection.password,
                )
                self.message_user(request, self.style.SUCCESS(f"Успешное подключение к {connection.url}/{connection.database}"), level=logging.INFO)
            except Exception as e:
                self.message_user(request, self.style.ERROR(f"Ошибка подключения к {connection.url}: {e}"), level=logging.ERROR)

