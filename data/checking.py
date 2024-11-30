from typing import Union
from aiogram import types
import logging

from aiogram.exceptions import TelegramBadRequest

async def check_subscription(user_id: int, channel: Union[str, int]) -> bool:
    """
    Foydalanuvchining kanalga obuna bo'lganligini tekshiradi.
    Agar obuna bo'lsa, True qaytaradi, aks holda False.
    """
    from app import bot  # Bot instance-ni import qilish

    try:
        # Foydalanuvchining holatini tekshirish
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True  # Foydalanuvchi kanalga obuna bo'lgan

    except TelegramBadRequest:
        logging.error(f"Xato: Foydalanuvchi kanalga obuna bo'lishi mumkin emas.")
        return False  # Kanalga obuna bo'lmagan yoki kanal mavjud emas

    # Agar foydalanuvchi obuna bo'lmagan bo'lsa, False qaytariladi
    return False
