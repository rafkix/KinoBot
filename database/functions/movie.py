from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.testing.plugin.plugin_base import logging

from database.database import async_session, engine
from database.models import Movie

import random
import string

def generate_movie_id():
    """4 raqam va 3 harfli movie_id generatsiyasi."""
    digits = ''.join(random.choices(string.digits, k=4))  # 4 ta raqam
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))  # 3 ta katta harf
    return digits + letters



async def add_movie(
        session: AsyncSession,
        movie_name: str,
        movie_lang: str,
        thumb: str,
        movie_code: str,
        movie_url: str,
        movie_count: int = 0
) -> str:
    new_movie = Movie(
        movie_id=generate_movie_id(),
        movie_name=movie_name,
        movie_lang=movie_lang,
        thumb = thumb,
        movie_code=movie_code,
        movie_url=movie_url,
        movie_time=datetime.now(),  # Use current datetime
        movie_count=movie_count
    )

    session.add(new_movie)
    try:
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"Kino qo'shishda xatolik: {e}")
        raise e
    return new_movie.movie_id


async def select_movie(movie_code: str, session: AsyncSession):
    # Create a SQLAlchemy select statement to fetch the movie by code
    stmt = select(Movie).filter_by(movie_code=movie_code)

    # Execute the statement
    result = await session.execute(stmt)

    # Get the first matching result (if any)
    movie = result.scalars().first()

    return movie

# Barcha kinolarni olish
async def all_movies(session: AsyncSession):
    result = await session.execute(select(Movie))
    return result.scalars().all()

# Kino ko‘rishlar sonini oshirish
async def increment_movie_count(session: AsyncSession, movie_id):
    movie = await select_movie(session, movie_id)
    if movie:
        movie.movie_count += 1
        await session.commit()
        return True
    return False

# Kinolar sonini hisoblash
async def count_movies(session: AsyncSession):
    result = await session.execute(select(func.count(Movie.movie_id)))
    return result.scalar()

# Kino ma'lumotini o‘chirish
async def delete_movie(session: AsyncSession, movie_id):
    movie = await select_movie(session, movie_id)
    if movie:
        await session.delete(movie)
        await session.commit()
        return True
    return False
