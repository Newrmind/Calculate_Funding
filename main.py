from Telegram_bot.aiogram_bot import run_bot, send_to_all_users
from get_cbr_prices import get_exchange_rates
from time_functions import check_time
from Funding.calculate_funding import calculate_funding
import asyncio

async def main():
    # Запуск бота в отдельном потоке
    run_bot()


    # Периодический запуск get_exchange_rates
    while True:
        if await check_time():
            print("Время считать фандинг.")
            exchange_rates = get_exchange_rates()

            message = "\n".join([f"{key}: {value}" for key, value in exchange_rates.items()])
            if message:
                await send_to_all_users(message)

            if exchange_rates:
                """Рассчитываем фандинг."""
                print(exchange_rates)

                tickers = ['USDRUBF', "EURRUBF"]
                for ticker in tickers:
                    funding_message = calculate_funding(symbol=ticker, cbr_prices=exchange_rates)
                    if message:
                        await send_to_all_users(funding_message)

        else:
            print("Сейчас выходной или вечерняя сессия.")

        await asyncio.sleep(5)  # Ждем перед следующим запросом

if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции
