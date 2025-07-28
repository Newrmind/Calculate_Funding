import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from Database.db_connection import db
from connection import bot_token, tg_admin_id
from Funding.data_storage import data_storage
import time_functions
from Telegram_bot.help_command import ADMIN_HELP_COMMAND


bot = Bot(token=bot_token)
dp = Dispatcher()

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

@dp.message(Command('help'))
async def handle_start(message: Message):
    user_id = message.from_user.id
    if user_id == tg_admin_id:
        try:
            await bot.send_message(chat_id=user_id, text=ADMIN_HELP_COMMAND, parse_mode=ParseMode.HTML)
        except Exception as e:
            await message.answer(f"Произошла ошибка: \n{e}")
            print(f"Ошибка: {e}")

@dp.message(Command('get_avg'))
async def handle_get_avg(message: Message):
    user_id = message.from_user.id
    if user_id == tg_admin_id:
        try:
            symbols = ["USDRUBF", "EURRUBF"]
            reply_lines = []

            for symbol in symbols:
                data = data_storage.get(symbol=symbol)

                if data is None:
                    reply_lines.append(f"🔹 *{symbol}*: _данные не найдены_")
                    continue

                timestamp = data["timestamp"]
                time_str = time_functions.timestamp_to_time(timestamp)
                avg_price = data["avg_price"]

                reply_lines.append(
                    f"🔹 *{symbol}*\n"
                    f"   • Средняя цена: *{avg_price:.6f}*\n"
                    f"   • Время запроса: _{time_str}_"
                )

            reply_message = "\n\n".join(reply_lines)
            await bot.send_message(chat_id=user_id, text=reply_message, parse_mode="Markdown")
        except Exception as e:
            await message.answer(f"Произошла ошибка: \n{e}")
            print(f"Ошибка: {e}")


@dp.message(Command('clear_requests_time'))
async def handle_clear_requests_time(message: Message):
    user_id = message.from_user.id
    if user_id == tg_admin_id:
        try:
            time_functions.request_time_change(db=db, request="cbr_prices_last_send", reset_time=True)
            time_functions.request_time_change(db=db, request="funding_last_send", reset_time=True)
            await bot.send_message(chat_id=user_id, text="Время запросов очищено!")
        except Exception as e:
            await message.answer(f"Произошла ошибка: \n{e}")
            print(f"Ошибка: {e}")

async def send_to_all_users(message: str, parse_mode: str = "Markdown"):
    users = db.get_all_users()
    chat_ids = [user[0] for user in users]

    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id, message, parse_mode=parse_mode)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")


# Функция для запуска бота
async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Функция для вызова start_bot() в существующем цикле событий
def run_bot():
    asyncio.get_event_loop().create_task(start_bot())  # Создаем задачу для асинхронного запуска

