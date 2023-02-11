import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
secret = os.getenv("secret_key")
admin_chat_id = os.getenv("chat_id")
