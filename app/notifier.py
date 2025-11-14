import requests
from app.config import NOTIFICATION_BACKEND, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class Notifier:
    def send(self, text: str):
        if NOTIFICATION_BACKEND == 'telegram' and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
            resp = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})
            if resp.status_code != 200:
                print('Telegram notification failed:', resp.text)
        else:
            print('NOTIFICATION:', text)

notifier = Notifier()
