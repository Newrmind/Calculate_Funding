from Telegram_bot.aiogram_bot import start_bot, send_to_all_users, send_to_admin
from Funding.get_cbr_prices import get_exchange_rates, format_exchange_rates_message
from time_functions import check_time, request_time_change, is_time_in_range
from Funding.calculate_funding import calculate_funding
from Funding.weighted_average_price import calculate_and_save_weighted_avg_price
from Funding.data_storage import data_storage
import asyncio
from Database.db_connection import db, db_creator
from datetime import datetime


def init():
    print("[INFO] Запуск функции init()", flush=True)
    # Создание базы данных
    db_creator.create_database("funding")
    db_creator.create_table_requests_time()
    db_creator.create_users_table()


async def main_loop():
    print("[INFO] Запуск функции main_loop()", flush=True)

    print("[INFO] Ожидание 3 секунд для инициализации бота...", flush=True)
    await asyncio.sleep(3)

    print(f"[DEBUG] data_storage ID в main.py: {id(data_storage)}", flush=True)

    iteration = 0

    while True:
        iteration += 1
        print(f"[DEBUG] Итерация цикла #{iteration}", flush=True)

        tickers = ['USDRUBF', "EURRUBF"]
        calculate_and_save_weighted_avg_price(tickers)

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

            print(f"[INFO] last_time_send_msg: {datetime.fromtimestamp(int(last_time_send_msg/1000))}", flush=True)
            need_send_exchange_rates = is_time_in_range(last_time_send_msg)
            print(f"[INFO] need_send_exchange_rates: {need_send_exchange_rates}", flush=True)

            print(f"[INFO] last_time_send_funding: {datetime.fromtimestamp(int(last_time_send_funding/1000))}", flush=True)
            need_send_funding = is_time_in_range(last_time_send_funding)
            print(f"[INFO] need_send_funding: {need_send_funding}", flush=True)



            # Запрашиваем курсы ЦБ
            if need_send_exchange_rates or need_send_funding:
                exchange_rates = get_exchange_rates()
                exchange_rates_message = None
                if exchange_rates:
                    exchange_rates_message = format_exchange_rates_message(exchange_rates)
                    print(f"[INFO] exchange_rates: {exchange_rates}")

                if need_send_exchange_rates and exchange_rates_message:
                    print("[INFO] Отправка сообщений с курсами валют.", flush=True)
                    # Отправляем сообщения с курсами.
                    print(exchange_rates_message)
                    await send_to_all_users(exchange_rates_message, parse_mode="HTML")
                    # Записываем время отправки сообщения
                    request_time_change(db=db, request="cbr_prices_last_send")

                # Рассчитываем фандинг.
                try:
                    if need_send_funding and exchange_rates:
                        any_funding_sent = False
                        print("[INFO] Отправка сообщений с фандингом.", flush=True)
                        funding_message_union = ""
                        print("[DEBUG] Перед входом в цикл фандинга", flush=True)
                        print(f"[DEBUG] data_storage keys: {list(data_storage._storage.keys())}", flush=True)
                        print(f"[DEBUG] data_storage content: {data_storage._storage}", flush=True)
                        for ticker in tickers:
                            data = data_storage.get(ticker)

                            print(f"[DEBUG] Получены данные от к data_storage.get(ticker): {data}")

                            if data is None:
                                warning_msg = f"[CRITICAL] Нет данных для тикера {ticker} в data_storage!"
                                print(warning_msg, flush=True)
                                await send_to_admin(warning_msg)
                                continue

                            avg_price_actual = is_time_in_range(data['timestamp'], start=(15, 30), end=(23, 59))
                            print(f"[DEBUG] avg_price_actual: {avg_price_actual}.")
                            if not avg_price_actual:
                                warning_msg = f"[WARNING] Нет средневзвешенной цены, рассчитанной после 15:30."
                                print(warning_msg)
                                await send_to_admin(message=warning_msg)
                                continue

                            funding_message_union += calculate_funding(symbol=ticker, cbr_prices=exchange_rates,
                                                                weighted_average_price=data['avg_price'])
                        if funding_message_union:
                            await send_to_all_users(funding_message_union)
                            any_funding_sent = True

                        # Записываем время отправки сообщения
                        if any_funding_sent:
                            request_time_change(db=db, request="funding_last_send")

                except Exception as e:
                    import traceback
                    error_msg = f"[CRITICAL] Исключение в блоке фандинга: {type(e).__name__}: {e}\n{traceback.format_exc()}"
                    print(error_msg, flush=True)
                    await send_to_admin(error_msg)

        else:
            print("[INFO] Сейчас не время расчёта фандинга.", flush=True)

        await asyncio.sleep(1)  # Ждем перед следующим запросом


async def main():
    print("[INFO] Запуск функции main()", flush=True)

    # Запускаем бота и основной цикл ПАРАЛЛЕЛЬНО
    bot_task = asyncio.create_task(start_bot())
    loop_task = asyncio.create_task(main_loop())

    await asyncio.gather(bot_task, loop_task)

if __name__ == "__main__":
    init()
    asyncio.run(main())  # Запуск основной функции
