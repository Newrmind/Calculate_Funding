from Telegram_bot.aiogram_bot import run_bot, send_to_all_users
from get_cbr_prices import get_exchange_rates
from time_functions import check_time
import asyncio

async def main():
    # Запуск бота в отдельном потоке
    run_bot()


    # Периодический запуск get_exchange_rates
    while True:
        if await check_time():
            print("Время считать фандинг.")
            message = get_exchange_rates()
            await send_to_all_users(message)
        else:
            print("Сейчас выходной или вечерняя сессия.")


        await asyncio.sleep(3600)  # Ждем 1 час перед следующим запросом

if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции
