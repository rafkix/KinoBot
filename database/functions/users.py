from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from database.models import User

# Foydalanuvchini qo'shish: Agar user allaqachon bazada bo‘lsa, yangi foydalanuvchi qo‘shilmaydi.
async def add_user(session: AsyncSession, user_id: int, full_name: str, referral: str, lang: str = "en"):
    # Foydalanuvchini tekshirish
    result = await session.execute(select(User).where(User.user_id == user_id))
    existing_user = result.scalars().first()

    if existing_user:
        return False  # Foydalanuvchi allaqachon mavjud

    # Foydalanuvchini qo'shish
    new_user = User(user_id=user_id, full_name=full_name, referral=referral, lang=lang)
    session.add(new_user)
    await session.commit()
    return True


# Foydalanuvchini ID bo‘yicha olish
async def select_user(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalars().first()

# Barcha foydalanuvchilarni olish
async def all_user(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()

# Foydalanuvchi tilini yangilash
async def update_lang(session: AsyncSession, user_id: int, new_lang: str):
    user = await select_user(session, user_id)
    if user:
        user.lang = new_lang
        await session.commit()
        return True
    return False

# Foydalanuvchilar sonini hisoblash
async def count_user(session: AsyncSession):
    result = await session.execute(select(func.count(User.user_id)))
    return result.scalar()

# Foydalanuvchini o'chirish
async def delete_user(session: AsyncSession, user_id: int):
    user = await select_user(session, user_id)
    if user:
        await session.delete(user)
        await session.commit()
        return True
    return False
