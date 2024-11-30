from aiogram.types import Message
from aiogram.filters import BaseFilter

class IsUserMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user is not None
