from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# User jadvali
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    lang = Column(String, default="uz")
    user_time = Column(DateTime, default=datetime.utcnow)
    referral = Column(Integer, ForeignKey("users.user_id"), nullable=True)

class Movie(Base):
    __tablename__ = 'movies'

    movie_id = Column(String, primary_key=True, index=True)
    movie_name = Column(String)
    movie_lang = Column(String)
    thumb = Column(String)
    movie_code = Column(String, unique=True, index=True)
    movie_url = Column(String)
    movie_count = Column(Integer, default=0)
    movie_time = Column(DateTime, nullable=True, default=func.now)

class Channel(Base):
    __tablename__ = 'channels'

    channel_id = Column(Integer, primary_key=True, autoincrement=True)  # Kanalning unikal ID si
    channel_link = Column(String, nullable=False)  # Kanalning havolasi
    channel_time = Column(DateTime, default=datetime.utcnow)  # Kanalga qo'shilgan vaqt
    is_private = Column(String)