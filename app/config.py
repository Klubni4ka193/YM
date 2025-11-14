from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./payments.db')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
NOTIFICATION_BACKEND = os.getenv('NOTIFICATION_BACKEND', 'console')
GATEWAY_MODE = os.getenv('GATEWAY_MODE', 'mock')

SCHEDULER_INTERVAL_SECONDS = int(os.getenv('SCHEDULER_INTERVAL_SECONDS', '60'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY_SECONDS', 86400)) 
