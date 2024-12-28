from aiogram import Bot
from asgiref.sync import async_to_sync, sync_to_async

import logging

from telegram_connector.models import BotSettings

logger = logging.getLogger(__name__)

async def send_telegram_message_async(message):
    try:
        settings = await sync_to_async(BotSettings.objects.filter(is_active=True).first)()
        if not settings:
            logger.warning("Нет активных настроек бота. Уведомления отключены.")
            return

        bot = Bot(token=settings.token)
        await bot.send_message(chat_id=settings.chat_id, text=message)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в Telegram: {e}")


def send_telegram_message(message):
    """
    Синхронная обертка для вызова асинхронной функции отправки сообщений.
    """
    try:
        async_to_sync(send_telegram_message_async)(message)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")