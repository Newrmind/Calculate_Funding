import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from Database.db_connection import db
from connection import bot_token

bot = Bot(token=bot_token)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command('start'))
async def handle_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    try:
        db.add_user(user_id=user_id, username=username)
        await message.answer(f"Привет, {username}! Вы подписаны на сообщения.")
    except Exception as e:
        await message.answer("Произошла ошибка при добавлении вас в базу данных.")
        print(f"Ошибка: {e}")


async def send_to_all_users(message: str):
    # Получаем список всех пользователей из базы данных
    users = db.get_all_users()
    chat_ids = [user[0] for user in users]

    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")


# Функция для запуска бота
async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Функция для вызова start_bot() в существующем цикле событий
def run_bot():
    asyncio.get_event_loop().create_task(start_bot())  # Создаем задачу для асинхронного запуска

