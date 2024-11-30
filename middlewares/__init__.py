from aiogram import Dispatcher

from .subscription import SubscriptionMiddleware
from .throttling import ThrottlingMiddleware

def setup(dp: Dispatcher):
    # dp.update.middleware(ThrottlingMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
