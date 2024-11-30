import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Botni sozlash
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

# Ma'lumotlarni tekshirish
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in the .env file.")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID not set in the .env file.")
if not CHANNEL_LINK:
    raise ValueError("CHANNEL_LINK not set in the .env file.")

print("Bot configuration loaded successfully.")
