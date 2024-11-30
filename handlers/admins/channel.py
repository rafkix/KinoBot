from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.inline import admin_panels, admin_channel

from app import bot
from data.config import ADMIN_ID
from database.database import async_session
from database.functions.channel import (
    add_channel,
    all_channels,
    delete_channel,
    count_channels,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

router = Router()

class AddChannelState(StatesGroup):
    channel_id = State()
    channel_link = State()
    channel_type = State()  # Add a state for channel type

@router.callback_query(lambda c: c.data == "add_channel")
async def start_add_channel(query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Kanal qo'shishni boshlash
    """
    await query.message.reply("📝 Kanal ID ni kiriting:")
    await state.set_state(AddChannelState.channel_id)

@router.message(AddChannelState.channel_id)
async def process_channel_id(message: types.Message, state: FSMContext) -> None:
    """
    Kanal ID ni qabul qilish
    """
    try:
        channel_id = int(message.text)
        await state.update_data(channel_id=channel_id)
        await message.reply("🔗 Kanal linkini kiriting:")
        await state.set_state(AddChannelState.channel_link)
    except ValueError:
        await message.reply("❌ Iltimos, to'g'ri kanal ID ni kiriting.")
@router.message(AddChannelState.channel_link)
async def process_channel_link(message: types.Message, state: FSMContext) -> None:
    """
    Kanal linkini qabul qilish
    """
    channel_link = message.text
    await state.update_data(channel_link=channel_link)

    await message.reply("🔐 Kanal turini tanlang:")

    # Set the next state for channel type
    await state.set_state(AddChannelState.channel_type)

@router.message(AddChannelState.channel_type)
async def process_channel_type(message: types.Message, state: FSMContext) -> None:
    """
    Handle the user's input for channel type: public or private.
    """
    # Handle both 'private' and 'public' inputs explicitly
    if message.text.strip().lower() == 'private':
        is_private = True
    elif message.text.strip().lower() == 'public':
        is_private = False
    else:
        await message.reply("❌ Iltimos, 'Private' yoki 'Public' ni yozing!")
        return  # If the user doesn't provide valid input, stop the process

    # Save the choice to the state
    await state.update_data(is_private=is_private)

    # Get all data from state (channel ID and link)
    data = await state.get_data()
    channel_id = data.get("channel_id")
    channel_link = data.get("channel_link")

    # Debugging: print values to check if data is correct
    print(f"Channel ID: {channel_id}, Channel Link: {channel_link}, Is Private: {is_private}")

    # Add the channel to the database
    async with async_session() as session:
        success = await add_channel(session, channel_id, channel_link, is_private=is_private)

    if success:
        # Notify success and show the admin panel
        await message.reply(
            f"✅ Kanal muvaffaqiyatli qo'shildi: {channel_id} ({'Maxfiy' if is_private else 'Ommaviy'})",
            reply_markup=await admin_channel(),
            disable_web_page_preview=True
        )
    else:
        # Notify failure if the channel already exists
        await message.reply(
            f"❌ Kanal allaqachon mavjud: {channel_id}",
            reply_markup=await admin_channel(),
            disable_web_page_preview=True
        )

    # End the FSM state
    await state.clear()


# Kanal sonini ko'rsatish
@router.callback_query(lambda c: c.data == "count_channels")
async def count_channels_callback(query: types.CallbackQuery):
    """
    Kanallar sonini qaytaradi.
    """
    async with async_session() as session:
        count = await count_channels(session)

    await query.message.edit_text(f"📊 Umumiy kanallar soni: {count}", reply_markup=await admin_channel(), disable_web_page_preview=True)


# Kanalni o'chirishni boshlash
@router.callback_query(lambda c: c.data == "delete_channel")
async def start_delete_channel(query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Kanallar ro'yxatini chiqarish va ularni o'chirish uchun tanlash
    """
    async with async_session() as session:
        channels = await all_channels(session=session)  # Barcha kanallarni olish

        if not channels:
            await query.answer("❌ Hech qanday kanal mavjud emas.")
            return

        keyboard = InlineKeyboardBuilder()  # InlineKeyboard uchun quruvchi

        # Har bir kanal uchun tugma yaratish
    for channel in channels:
        try:
            # Fetch channel details using the channel ID (get_chat will retrieve channel info including title)
            chat_info = await bot.get_chat(channel.channel_id)
            channel_title = chat_info.title  # Get the channel's title
            
            # Add a button with the channel title as text and callback data to confirm deletion
            keyboard.button(
                text=f"{channel_title}",  # Use channel title for the button text
                callback_data=f"confirm_delete:{channel.channel_id}"  # Callback for confirming deletion
            )

        except Exception as e:
            # Handle errors (e.g., bot might not have permission to access the channel)
            print(f"Error fetching channel info for {channel.channel_id}: {e}")
            keyboard.button(
                text=f"{channel.channel_id}",  # If there's an error, display a fallback text
                callback_data=f"confirm_delete:{channel.channel_id}"
            )

        # Tugmalarni tekislash (1 ustunli layout)
        keyboard.adjust(1)

        await query.message.edit_text(
            "Kanallar ro'yxatini tanlang va o'chirishni tasdiqlang:", reply_markup=keyboard.as_markup()
        )
        await query.answer()  # Callbackni tasdiqlash

# Kanalni o'chirish uchun tasdiqlash tugmasi
def build_confirmation_keyboard(channel_id):
    keyboard = InlineKeyboardBuilder()  # InlineKeyboard uchun quruvchi

    keyboard.button(
        text="Ha", 
        callback_data=f"delete_channel:{channel_id}"  # Kanalni o'chirish
    )
    keyboard.button(
        text="Yo'q", 
        callback_data="cancel_delete"  # O'chirishni bekor qilish
    )

    return keyboard.as_markup()  # Tasdiqlash tugmasini qaytarish

# Kanalni o'chirishni tasdiqlash
@router.callback_query(F.data.startswith('confirm_delete:'))
async def handle_confirm_delete_callback(callback_query: types.CallbackQuery):
    channel_id = int(callback_query.data.split(':')[1])  # Kanal ID sini olish

    # Tasdiqlash uchun klaviatura yaratish
    confirmation_keyboard = build_confirmation_keyboard(channel_id)

    await callback_query.message.edit_text(
        f"Siz id bilan kanalni o'chirishga ishonchingiz komilmi? {channel_id}?",
        reply_markup=confirmation_keyboard
    )
    await callback_query.answer()  # Callbackni tasdiqlash

# Kanalni o'chirishni amalga oshirish
@router.callback_query(F.data.startswith('delete_channel:'))
async def handle_delete_channel_callback(callback_query: types.CallbackQuery):
    # Only allow the admin to delete the channel
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ Yu bu amalni bajarish uchun ruxsatga ega emas.")
        return

    channel_id = int(callback_query.data.split(':')[1])  # Get the channel ID from the callback

    # Ensure `delete_channel` is called with the correct session and channel_id
    async with async_session() as session:
        success = await delete_channel(session, channel_id)  # Pass the session and channel_id

    if success:
        await callback_query.message.edit_text(f"✅ ID bilan kanali {channel_id} biz o'chirildik.", reply_markup=await admin_channel(), disable_web_page_preview=True)
    else:
        await callback_query.message.edit_text(f"❌ Kanalni oʻchirishda xatolik yuz berdi.", reply_markup=await admin_channel(), disable_web_page_preview=True)
    
    await callback_query.answer()  # Confirm callback


# Optional: Handler to cancel deletion
@router.callback_query(F.data == "cancel_delete")
async def handle_cancel_delete(callback_query: types.CallbackQuery):
    await callback_query.answer("Deletion canceled.")
    await callback_query.message.edit_text("Kanalni o'chirish jarayoni bizni kanzel qildi.")