import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PRODAMUS_API_KEY = os.getenv("PRODAMUS_API_KEY")
PRICE = int(os.getenv("PRICE", 1490))  # По умолчанию 1490 рублей