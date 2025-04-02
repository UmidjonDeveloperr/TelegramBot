import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, ADMIN_ID
from handlers import router
from flask import Flask

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Flask ilovasini yaratish
app = Flask(__name__)

async def main():
    try:
        # Bot va Dispatcher yaratish
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()

        # Routerlarni yuklash (admin birinchi, keyin user)
        dp.include_router(router)

        # Eski updateslarni tozalash
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Bot ishga tushdi...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Botda xatolik yuz berdi: {e}", exc_info=True)
    finally:
        if 'bot' in locals():
            await bot.session.close()
            logger.info("Bot sessiyasi yopildi")

@app.route("/")  # Flask uchun yo'l
def index():
    return "Bot is running!"  # Sahifa haqida ma'lumot

if __name__ == "__main__":
    try:
        # Botni asyncio yordamida ishga tushirish
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))  # Portni o'rnatish
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
    except Exception as e:
        logger.critical(f"Kutilmagan xatolik: {e}", exc_info=True)
