import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# O'zgaruvchilarni olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///test_datas.db")  # Default SQLite
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Agar ADMIN_ID mavjud bo'lmasa, 0 qo'yiladi

# Tekshirish
print(f"Bot token: {BOT_TOKEN}")
print(f"Database URL: {DATABASE_URL}")
print(f"Admin ID: {ADMIN_ID}")
