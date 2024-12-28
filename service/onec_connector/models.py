from django.db import models

# Create your models here.
class OneCConfiguration(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название конфигурации")
    description = models.TextField(blank=True, verbose_name="Описание")
    active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Конфигурация 1С"
        verbose_name_plural = "Конфигурации 1С"

    def __str__(self):
        return self.name


class OneCConnection(models.Model):
    config = models.ForeignKey(OneCConfiguration, on_delete=models.CASCADE, related_name='connections',
                               verbose_name="Конфигурация")
    url = models.URLField(verbose_name="URL сервера 1С")
    username = models.CharField(max_length=50, verbose_name="Имя пользователя")
    password = models.CharField(max_length=100, verbose_name="Пароль")
    database = models.CharField(max_length=100, verbose_name="Название базы данных")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Подключение к 1С"
        verbose_name_plural = "Подключения к 1С"

    def __str__(self):
        return f"{self.config.name} - {self.url}"