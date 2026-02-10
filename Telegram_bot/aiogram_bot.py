import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
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
    """Отправка сообщения всем пользователям с обработкой исключений"""
    users = db.get_all_users()

    if not users:
        print("[INFO] Нет пользователей для отправки сообщений")
        return

    successful_sends = 0
    failed_sends = 0

    for user in users:
        chat_id = user[0]  # user[0] - это user_id
        try:
            await bot.send_message(chat_id, message, parse_mode=parse_mode)
            successful_sends += 1
            await asyncio.sleep(0.05)  # Небольшая задержка между сообщениями
        except TelegramForbiddenError:
            # Пользователь заблокировал бота - удаляем из БД
            print(f"[WARNING] Пользователь {chat_id} заблокировал бота. Удаляем из БД.")
            db.delete_user(chat_id)
            failed_sends += 1
        except TelegramBadRequest as e:
            # Другие ошибки Telegram API (например, неверный chat_id)
            if "chat not found" in str(e).lower() or "user not found" in str(e).lower():
                print(f"[WARNING] Пользователь {chat_id} не найден. Удаляем из БД.")
                db.delete_user(chat_id)
            else:
                print(f"[ERROR] Ошибка отправки пользователю {chat_id}: {e}")
            failed_sends += 1
        except Exception as e:
            # Все остальные исключения
            print(f"[ERROR] Неожиданная ошибка для пользователя {chat_id}: {e}")
            failed_sends += 1

    # Логируем результаты отправки
    print(f"[INFO] Отправка завершена: успешно {successful_sends}, неудачно {failed_sends}")

    # Если все отправки провалились, отправляем уведомление администратору
    if successful_sends == 0 and failed_sends > 0:
        await send_to_admin(f"⚠️ Все отправки провалились! Проверьте статус бота.")


async def send_to_admin(message: str):
    """Отправка сообщения администратору с обработкой исключений"""
    try:
        await bot.send_message(tg_admin_id, message)
    except TelegramForbiddenError:
        print(f"[CRITICAL] Администратор {tg_admin_id} заблокировал бота!")
    except Exception as e:
        print(f"[ERROR] Ошибка при отправке сообщения админу {tg_admin_id}: {e}")


async def send_to_admin(message: str):
    try:
        await bot.send_message(tg_admin_id, message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения админу {tg_admin_id}: {e}")


# Функция для запуска бота
async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


