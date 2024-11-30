from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from database.models import Channel  # O'zgartiring, to'g'ri modelni import qiling

# Kanal qo‘shish
async def add_channel(session: AsyncSession, channel_id: int, channel_link: str, is_private: bool):
    # Kanal bazada bor yoki yo'qligini tekshirish
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing_channel = result.scalars().first()

    if existing_channel:
        return False  # Kanal allaqachon mavjud

    # Yangi kanal qo‘shish
    new_channel = Channel(channel_id=channel_id, channel_link=channel_link, is_private=is_private)
    session.add(new_channel)
    await session.commit()
    return True

# Kanal ma'lumotini olish
async def select_channel(channel_id: int, session: AsyncSession):
    stmt = select(Channel).filter_by(channel_id=channel_id)

    # Execute the statement
    result = await session.execute(stmt)

    # Get the first matching result (if any)
    channel = result.scalars().first()

    return channel

# Barcha kanallarni olish
async def all_channels(session: AsyncSession):
    result = await session.execute(select(Channel))
    return result.scalars().all()

# Kanal ma'lumotini yangilash
async def update_channel(session: AsyncSession, channel_id: int, new_link: str):
    channel = await select_channel(channel_id, session)  # Fix argument order here
    if channel:
        channel.channel_link = new_link
        await session.commit()
        return True
    return False

# Kanallar sonini hisoblash
async def count_channels(session: AsyncSession):
    result = await session.execute(select(func.count(Channel.channel_id)))
    return result.scalar()

async def delete_channel(session: AsyncSession, channel_id: int):
    channel = await select_channel(channel_id, session)  # Fix argument order here
    if channel:
        await session.delete(channel)
        await session.commit()
        return True
    return False
