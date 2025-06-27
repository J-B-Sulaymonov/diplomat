import requests
from django.conf import settings


def send_telegram_message(message, chat_id=settings.TELEGRAM_CHAT_ID, message_id=None, img_url=None):
    """Telegramga xabar yuborish yoki tahrirlash funktsiyasi."""
    bot_token = settings.TELEGRAM_BOT_TOKEN

    if img_url:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        params = {
            "chat_id": chat_id,
            "photo": img_url,  # Rasm URL yoki faylni yuborish
            "caption": message,  # Xabar
        }
    else:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message,
        }

    # Telegram API'ga so'rov yuborish
    response = requests.get(url, params=params)

    # So'rov javobini konsolga chiqarish
    print(response.json())  # Bu yerda Telegram API'dan qaytgan javobni tekshirasiz

    return response
