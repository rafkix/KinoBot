from aiogram import Router, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.testing.plugin.plugin_base import logging
from middlewares.subscription import SubscriptionMiddleware

import asyncio
from app import bot
from data.checking import check_subscription
from data.config import ADMIN_ID
from database.database import async_session  # Sessiya generatorini import qiling
from database.functions.channel import all_channels
from database.functions.users import add_user
from keyboards.inline import menu

router = Router()


@router.message(CommandStart())
async def hello_bot(message: Message, command: CommandObject):
    user_info = message.from_user
    # Deep link parametrini olish
    payload = command.args
    referral = payload if payload else None

    # AsyncSession ni ishlatish
    async with async_session() as session:
        # Foydalanuvchini qo'shish
        await add_user(
            session=session,
            user_id=user_info.id,
            full_name=user_info.full_name or "No Name",
            lang=user_info.language_code or "en",
            referral=referral
        )

    # Menu yaratish
    markup_start = await menu()

    # Foydalanuvchiga xush kelibsiz xabarini yuborish
    await message.answer(
        text="""<b>👋 Assalomu alaykum рафких botimizga xush kelibsiz.

✍🏻 Kino kodini yuboring.</b>""",
        reply_markup=markup_start  # Inline keyboard ni yuborish
    )

