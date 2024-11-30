from aiogram.filters import Command

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from data.config import ADMIN_ID
from database.database import async_session
from database.functions.channel import all_channels
from database.functions.users import count_user
from filters.is_admin import IsAdmin
from keyboards.inline import admin_panels, admin_channel

router = Router()



@router.message(Command("admin"), IsAdmin(ADMIN_ID))
async def admin_panel_handler(message: Message):
    text = "〽️ Siz admin paneldasiz kerakli menu tanlang:"
    reply_markup = await admin_panels()
    await message.answer(text=text, reply_markup=reply_markup)


@router.callback_query(lambda c: c.data == "admin", IsAdmin(ADMIN_ID))
async def admin_panel_handler(query: CallbackQuery):
    text = "🔙 Asosiy menyuga qaytdingiz. Tanlang:"
    reply_markup = await admin_panels()

    await query.message.edit_text(text=text, reply_markup=reply_markup)


# 1. **Kanallarni ko'rsatish handleri**
@router.callback_query(lambda c: c.data == "view_channels", IsAdmin(ADMIN_ID))
async def view_channels_handler(callback: CallbackQuery):
    async with async_session() as session:
        channels = await all_channels(session)  # Barcha kanallarni olish
        if channels:
            text = "<b>📋 Kanallar ro'yxati:</b>\n\n"
            for index, channel in enumerate(channels, start=1):
                text += f"{index}. {channel.channel_link}\n"
        else:
            text = "📋 Kanallar mavjud emas."
    await callback.message.edit_text(text, reply_markup=await admin_channel(), disable_web_page_preview=True)


@router.callback_query(lambda c: c.data == "view_users_count", IsAdmin(ADMIN_ID))
async def view_users_count_handler(callback: CallbackQuery):
    async with async_session() as session:
        user_count = await count_user(session)  # Foydalanuvchilar sonini hisoblash
        text = f"<b>👥 Foydalanuvchilar soni:</b> {user_count}"
    await callback.message.edit_text(text, reply_markup=await admin_panels())

