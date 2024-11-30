# from aiogram.filters import Command

# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery

# from data.config import ADMIN_ID
# from database.database import async_session
# from database.functions.channel import all_channels
# from database.functions.users import all_user
# from filters.is_admin import IsAdmin
# from keyboards.inline import admin_panels, admin_channel

# router = Router()

# # 3. **Xabar yuborish handleri**
# @router.callback_query(lambda c: c.data == "send_message", IsAdmin(ADMIN_ID))
# async def send_message_handler(callback: CallbackQuery):
#     text = (
#         "<b>📨 Xabar yuborish:</b>\n\n"
#         "Xabar matnini kiriting va yuborish uchun tasdiqlang."
#     )
#     await callback.message.edit_text(text, reply_markup=None)  # Xabar yuborish bosqichiga o'tish