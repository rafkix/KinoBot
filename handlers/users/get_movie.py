from venv import logger

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from database.database import async_session
from database.functions.movie import select_movie  # Make sure to import the select_movie function

router = Router()


@router.message(F.content_type == 'text')
async def handle_movie_code(message: Message):
    movie_code = message.text  # Extract the movie code from the message text

    async with async_session() as session:
        # Call the select_movie function with the movie_code and session
        movie = await select_movie(movie_code, session)

        # Check if movie is found and send a response
        if movie:
            # Ko'rishlar sonini oshirish va o'zgarishlarni bazaga saqlash
            movie.movie_count += 1
            session.add(movie)
            await session.commit()  # O'zgarishlarni bazaga yuborish

            # Inline tugmalarni yaratish: O'chirish
            inline_buttons = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📤 Do'stlarga yuborish",
                                             switch_inline_query=f"{movie.movie_code}"),
                    ],
                    [
                        InlineKeyboardButton(text="❌", callback_data=f"delete")
                    ]
                ]
            )

            # Javob xabarini formatlash
            response = (
                f"🎬 Kino: {movie.movie_name}\n"
                f"🌐 Til: {movie.movie_lang}\n"
                f"👀 Ko'rishlar soni: {movie.movie_count}\n"
            )
            if movie.movie_time:
                response += f"⏰ Qo'shilgan vaqt: {movie.movie_time}\n"

            await message.reply_video(
                video=movie.movie_url,
                caption=response,
                reply_markup=inline_buttons  # Inline tugmalar bilan javob yuborish
            )
            logger.info(f"Kino topildi va ko'rishlar soni oshirildi: {movie.movie_name}")

        else:
            await message.answer("Bunday kodli kinomavjud emas!")

@router.callback_query(F.data == "delete")
async def delete_movie_handler(query: Message):
    await query.message.delete()