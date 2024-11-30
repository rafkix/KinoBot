from aiogram.fsm.state import State, StatesGroup


class AddMovieState(StatesGroup):
    waiting_for_video = State()
    waiting_for_name = State()
    waiting_for_lang = State()
    waiting_for_thumbnail = State()
