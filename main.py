from Telegram_bot.aiogram_bot import run_bot, send_to_all_users
from get_cbr_prices import get_exchange_rates
from time_functions import check_time, request_time_change, is_time_in_range
from Funding.calculate_funding import calculate_funding
import asyncio
from Database.db_connection import db, db_creator

async def main():
    print("[INFO] Запуск функции main()", flush=True)
    # Создание базы данных
    db_creator.create_database("funding")
    db_creator.create_table_requests_time()
    db_creator.create_users_table()

    # Запуск бота
    run_bot()

    while True:
        if await check_time():
            print("[INFO] Время расчёта фандинга.", flush=True)

            # Проверяем, было ли отправлено сегодня сообщение с курсами ЦБ.
            last_time_send_db_response = db.get_table_from_db("SELECT timestamp FROM requests_time \
                                                 WHERE request = 'cbr_prices_last_send'")
            if not last_time_send_db_response.empty:
                last_time_send_msg = int(last_time_send_db_response.loc[0, 'timestamp'])
                print(last_time_send_msg)
            else:
                last_time_send_msg = 9121
                print(last_time_send_msg)

            need_send = is_time_in_range(last_time_send_msg)

            # Запрашиваем курсы ЦБ
            exchange_rates = get_exchange_rates()
            print(exchange_rates)

            if (exchange_rates and need_send) or last_time_send_msg == 9121:
                print("[INFO] Отправка сообщений", flush=True)
                # Отправляем сообщения с курсами.
                message = "\n".join([f"{key}: {value}" for key, value in exchange_rates.items()])
                if message:
                    await send_to_all_users(message)
                    # Записываем время отправки сообщения
                    request_time_change(db=db, request="cbr_prices_last_send")

                # Рассчитываем фандинг.
                tickers = ['USDRUBF', "EURRUBF"]
                for ticker in tickers:
                    funding_message = calculate_funding(symbol=ticker, cbr_prices=exchange_rates)
                    if funding_message:
                        await send_to_all_users(funding_message)

        else:
            print("[INFO] Сейчас не время расчёта фандинга.", flush=True)

        await asyncio.sleep(15)  # Ждем перед следующим запросом

if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции
