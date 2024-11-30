from aiogram import Dispatcher

from handlers import users, admins


def setup(dp: Dispatcher):
    admins.setup(dp)
    users.setup(dp)
