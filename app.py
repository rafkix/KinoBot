import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.orm.sync import update

import handlers
import middlewares
from data import config
from data.config import ADMIN_ID
from database.database import init_db

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def main():
    await init_db()
    handlers.setup(dp)  # Setup handlers
    middlewares.setup(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(
        chat_id=config.ADMIN_ID,
        text="Bot ishga tushdi"
    )
    # Start polling (or another method to start the bot)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
               "[%(asctime)s] - %(name)s - %(message)s",
    )

    logger.info("Starting bot")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi")
    finally:
        asyncio.run(bot.session.close())  # Ensure the bot session is closed
