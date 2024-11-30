import logging
from aiogram import Router, F, types
from aiogram.types import InlineQueryResultVideo, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from database.database import async_session
from database.functions.movie import select_movie  # Ensure the function is properly imported

router = Router()

@router.inline_query(F.query != "")
async def inline_query_handler(query: types.InlineQuery):
    movie_code = query.query.strip()  # Get the text of the inline query and remove unnecessary spaces

    async with async_session() as session:
        # Fetch the movie based on the code
        movie = await select_movie(movie_code, session)

        if movie:
            # Increment view count and commit changes to the database
            movie.movie_count += 1
            session.add(movie)
            await session.commit()

            # Create inline buttons for sharing and deleting
            inline_buttons = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📤 Do'stlarga yuborish",
                            switch_inline_query=f"{movie.movie_code}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ O'chirish",
                            callback_data=f"delete_{movie.movie_code}"
                        )
                    ]
                ]
            )

            # Validate thumbnail URL
            if not movie.thumb:
                logging.warning(f"No thumbnail found for movie {movie.movie_code}")
                thumb_url = "https://uzmovi.tv/images/fordok-min.jpg"  # Use a default thumbnail
            else:
                thumb_url = movie.thumb

            # Create InlineQueryResultVideo to send the video as a result
            result = InlineQueryResultVideo(
                id=movie.movie_code,  # Unique identifier for the result
                video_url=movie.movie_url,  # The direct video link
                mime_type="video/mp4",  # Video MIME type (adjust if necessary)
                thumbnail_url='https://m.media-amazon.com/images/M/MV5BZjU3ZDRmNjEtNzA3Zi00ZWIxLWI3NjItYzA0MjgzNWI5YzBkXkEyXkFqcGdeQXVyMjUyNDk2ODc@._V1_.jpg',  # Correct thumbnail URL
                title=movie.movie_name,  # Title displayed in the inline query
                description=movie.movie_name,  # Description for the result
                thumb_url=thumb_url,
                caption=(
                    f"🎬 Kino: {movie.movie_name}\n"
                    f"🌐 Til: {movie.movie_lang}\n"
                    f"👀 Ko'rishlar soni: {movie.movie_count}\n"
                ),
                reply_markup=inline_buttons  # Attach inline buttons
            )

            # Answer the inline query with the result
            await query.answer([result], cache_time=0)
        else:
            # No results found, return an empty list
            await query.answer([], cache_time=0)
