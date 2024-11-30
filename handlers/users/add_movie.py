import random
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from data.config import ADMIN_ID, CHANNEL_LINK
from database.database import async_session
from database.functions.movie import add_movie
from states import AddMovieState
from app import bot
import logging

router = Router()


@router.callback_query(F.data == "start_add_movie")
async def start_movie_addition(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        text="📋 Iltimos kinoni yuboring:"
    )
    await state.set_state(AddMovieState.waiting_for_video)
    await callback_query.answer()


@router.message(AddMovieState.waiting_for_video, F.content_type == "video")
async def handle_video_post(message: Message, state: FSMContext):
    video = message.video.file_id
    sent_message = await bot.send_video(
        chat_id=f"@{CHANNEL_LINK}", video=video
    )
    video_url = f"https://t.me/{CHANNEL_LINK}/{sent_message.message_id}"
    await message.answer(
        text=f"🔔 Video yuborildi.\nURL: {video_url}\n📋 Iltimos, kinoning nomini kiriting:"
    )
    await state.update_data(video_url=video)
    await state.set_state(AddMovieState.waiting_for_name)


@router.message(AddMovieState.waiting_for_name)
async def get_movie_name(message: Message, state: FSMContext):
    await state.update_data(movie_name=message.text)
    await state.set_state(AddMovieState.waiting_for_lang)
    await message.answer("📖 Iltimos, kinoning tilini kiriting (masalan: EN, UZ, RU):")


@router.message(AddMovieState.waiting_for_lang)
async def get_movie_lang(message: Message, state: FSMContext):
    data = await state.get_data()
    movie_name = data['movie_name']
    movie_lang = message.text.upper()

    valid_languages = ["EN", "UZ", "RU"]
    if movie_lang not in valid_languages:
        await message.answer("❌ Iltimos, faqat EN, UZ, yoki RU tillarini kiriting.")
        return

    await state.update_data(movie_lang=movie_lang)
    await state.set_state(AddMovieState.waiting_for_thumbnail)
    await message.answer("📸 Iltimos, kinoning rasmni yuboring:")


@router.message(AddMovieState.waiting_for_thumbnail, F.content_type == "photo")
async def get_movie_thumbnail(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id  # Get the file_id of the largest size of the photo
    await state.update_data(thumbnail=photo)

    await message.answer("🔔 Rasm qabul qilindi. Ma'lumotlar saqlanmoqda...")
    await save_movie_info(message, state)


async def save_movie_info(message: Message, state: FSMContext):
    data = await state.get_data()
    video_url = data['video_url']
    movie_name = data['movie_name']
    movie_lang = data['movie_lang']
    thumb = data['thumbnail']

    def generate_movie_code():
        """Generate a random numeric movie code between 1 and 9999."""
        return str(random.randint(1, 999))

    movie_code = generate_movie_code()

    try:
        async with async_session() as session:
            movie_id = await add_movie(
                session=session,
                movie_code=movie_code,
                movie_name=movie_name,
                movie_lang=movie_lang,
                thumb=thumb,
                movie_url=video_url,
                movie_count="0"
            )
        await message.answer_photo(
            photo=thumb,
            caption=f"✅ Kino muvaffaqiyatli qo'shildi:\n"
                             f"🎬 Nom: {movie_name}\n"
                             f"🌐 Til: {movie_lang}\n"
                             f"🔑 Kod: {movie_code}\n"
                             f"🆔 ID: {movie_id}"
        )
    except Exception as e:
        logging.error(f"Kino qo'shishda xatolik: {e}")
        await message.answer("❌ Kino qo'shishda xatolik yuz berdi. Iltimos, keyinroq sinab ko'ring.")

    await state.clear()
