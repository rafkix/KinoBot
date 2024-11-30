from aiogram import Dispatcher

from .panel import router as start_router
from .channel import router as channel_router


def setup(dp: Dispatcher):
    dp.include_routers(
        start_router,
        channel_router
    )