from typing import Callable, Awaitable, Any, Dict, Union
from aiogram import BaseMiddleware, types
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.checking import check_subscription  # Import the subscription check function
from database.database import async_session
from database.functions.channel import all_channels


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self):
        self.channels_info = []
        asyncio.create_task(self.load_channels())  # Load channels

    async def load_channels(self):
        """
        Load all necessary channels from the database.
        """
        async with async_session() as session:
            self.channels_info = await all_channels(session)

    async def check_user_subscription(self, user_id: int) -> Union[InlineKeyboardMarkup, None]:
        """
        Check if the user is subscribed to all public channels.
        If not subscribed, return an inline keyboard with the channel links.
        If the channel is private, show the button but do not check subscription.
        """
        builder = InlineKeyboardBuilder()
        subscription_status = True

        for channel in self.channels_info:
            # Check if the channel is private
            is_private = channel.is_private == "1"  # Assuming `is_private` indicates if the channel is private

            if is_private:
                # For private channels, just add the button without checking subscription
                builder.button(
                    text=f"➕ Obuna Bo'ling)",
                    url=f"{channel.channel_link}"
                )
                continue  # Skip checking subscription for private channels

            # For public channels, use the `check_subscription` method
            is_subscribed = await check_subscription(user_id, channel.channel_id)
            subscription_status &= is_subscribed

            if not is_subscribed:  # Add the subscription button for channels the user is not subscribed to
                builder.button(
                    text=f"➕ Obuna Bo'ling",
                    url=f"{channel.channel_link}"
                )

        if not subscription_status:  # If not all public subscriptions are active, add a confirmation button
            builder.button(
                text="A'zo bo'ldim ✅",
                callback_data="check"
            )
            builder.adjust(1)
            return builder.as_markup()

        return None  # If the user is subscribed to all public channels, return None

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Union[Message, CallbackQuery],
                       data: Dict[str, Any]) -> Any:
        """
        Check user subscription before processing the request.
        """
        if isinstance(event, types.Message):
            user_id = event.from_user.id
            chat_id = event.chat.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id
            chat_id = event.message.chat.id
        else:
            return await handler(event, data)

        from app import bot  # Import the bot instance

        # Check user subscription
        keyboard = await self.check_user_subscription(user_id)

        if keyboard:
            await bot.send_message(
                chat_id,
                text=(  # Message when the user is not subscribed
                    "<b>❌ Kechirasiz, botimizdan foydalanish uchun quyidagi kanallarga a'zo bo'lishingiz kerak:</b>\n\n"
                    "Iltimos, obuna bo'ling va qayta tekshiring."
                ),
                reply_markup=keyboard
            )
            return CancelHandler()

        # If the user is subscribed to all public channels, proceed with the handler
        return await handler(event, data)
