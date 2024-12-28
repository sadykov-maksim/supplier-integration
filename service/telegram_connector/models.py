from django.db import models

# Create your models here.
class BotSettings(models.Model):
    name = models.CharField(max_length=255, default="Default Bot")
    token = models.CharField(max_length=255, help_text="Telegram Bot Token")
    chat_id = models.CharField(max_length=255, help_text="Chat ID для отправки уведомлений")
    is_active = models.BooleanField(default=True, help_text="Включить отправку уведомлений")

    def __str__(self):
        return self.name