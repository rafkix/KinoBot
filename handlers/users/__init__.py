from aiogram import Dispatcher

from .start import router as start_router
from .add_movie import router as add_router
from .get_movie import router as get_router
from .search_query import router as search_router


def setup(dp: Dispatcher):
    dp.include_routers(
        start_router,
        add_router,
        get_router,
        search_router
    )