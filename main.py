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
            else:
                last_time_send_msg = 999

            last_time_send_funding = db.get_table_from_db("SELECT timestamp FROM requests_time \
                                                             WHERE request = 'funding_last_send'")

            if not last_time_send_funding.empty:
                last_time_send_funding = int(last_time_send_funding.loc[0, 'timestamp'])
            else:
                last_time_send_funding = 999

            print(f"[INFO] last_time_send_msg: {last_time_send_msg}", flush=True)
            need_send_exchange_rates = is_time_in_range(last_time_send_msg)
            print(f"[INFO] need_send_exchange_rates: {need_send_exchange_rates}", flush=True)

            print(f"[INFO] last_time_send_funding: {last_time_send_funding}", flush=True)
            need_send_funding = is_time_in_range(last_time_send_funding)
            print(f"[INFO] need_send_exchange_rates: {need_send_funding}", flush=True)

            # Запрашиваем курсы ЦБ
            if need_send_exchange_rates or need_send_funding:
                exchange_rates = get_exchange_rates()
                print(f"[INFO] exchange_rates: {exchange_rates}")

                if need_send_exchange_rates and exchange_rates:
                    print("[INFO] Отправка сообщений с курсами валют.", flush=True)
                    # Отправляем сообщения с курсами.

                    message = "\n".join([f"{key}: {value}" for key, value in exchange_rates.items()])
                    print(message)
                    await send_to_all_users(message)
                    # Записываем время отправки сообщения
                    request_time_change(db=db, request="cbr_prices_last_send")

                    # Рассчитываем фандинг.
                    tickers = ['USDRUBF', "EURRUBF"]
                    if need_send_funding:
                        print("[INFO] Отправка сообщений с фандингом.", flush=True)
                        for ticker in tickers:
                            funding_message = calculate_funding(symbol=ticker, cbr_prices=exchange_rates)
                            if funding_message:
                                await send_to_all_users(funding_message)
                                # Записываем время отправки сообщения
                                request_time_change(db=db, request="funding_last_send")

        else:
            print("[INFO] Сейчас не время расчёта фандинга.", flush=True)

        await asyncio.sleep(15)  # Ждем перед следующим запросом

if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции
