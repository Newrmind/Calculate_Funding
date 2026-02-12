from Telegram_bot.aiogram_bot import start_bot, send_to_all_users, send_to_admin
from Funding.get_cbr_prices import get_exchange_rates, format_exchange_rates_message
from time_functions import check_time, request_time_change, is_time_in_range
from Funding.calculate_funding import calculate_funding
from Funding.weighted_average_price import calculate_and_save_weighted_avg_price
from Funding.data_storage import data_storage
import asyncio
import signal
import sys
from Database.db_connection import db, db_creator
from datetime import datetime

# Глобальные переменные для управления задачами
shutdown_event = asyncio.Event()
tasks = []


def init():
    print("[INFO] Запуск функции init()", flush=True)
    # Создание базы данных
    db_creator.create_database("funding")
    db_creator.create_table_requests_time()
    db_creator.create_users_table()


def signal_handler():
    """Обработчик сигналов для graceful shutdown"""
    print("\n[INFO] Получен сигнал завершения. Завершение работы...", flush=True)
    shutdown_event.set()


async def main_loop():
    print("[INFO] Запуск функции main_loop()", flush=True)
    print("[INFO] Ожидание 3 секунд для инициализации бота...", flush=True)

    try:
        await asyncio.sleep(3)
    except asyncio.CancelledError:
        print("[INFO] main_loop(): задача отменена во время ожидания", flush=True)
        return

    iteration = 0

    while not shutdown_event.is_set():
        try:
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

                print(f"[INFO] last_time_send_msg: {datetime.fromtimestamp(int(last_time_send_msg / 1000))}",
                      flush=True)
                need_send_exchange_rates = is_time_in_range(last_time_send_msg)
                print(f"[INFO] need_send_exchange_rates: {need_send_exchange_rates}", flush=True)

                print(f"[INFO] last_time_send_funding: {datetime.fromtimestamp(int(last_time_send_funding / 1000))}",
                      flush=True)
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
                    if need_send_funding and exchange_rates:
                        any_funding_sent = False
                        print("[INFO] Отправка сообщений с фандингом.", flush=True)
                        funding_message_union = ""
                        for ticker in tickers:
                            print("[DEBUG] Обращение к data_storage.get(ticker)")
                            data = data_storage.get(ticker)
                            print(f"[DEBUG] Получены данные от к data_storage.get(ticker): {data}")
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

            else:
                print("[INFO] Сейчас не время расчёта фандинга.", flush=True)

            # Используем wait с таймаутом вместо sleep
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                continue  # Продолжаем цикл

        except asyncio.CancelledError:
            print("[INFO] main_loop(): задача отменена", flush=True)
            break
        except Exception as e:
            print(f"[ERROR] Ошибка в main_loop: {e}", flush=True)
            await asyncio.sleep(1)

    print("[INFO] main_loop(): завершение работы", flush=True)


async def shutdown(signal_name=None):
    """Graceful shutdown"""
    print(f"\n[INFO] Получен сигнал {signal_name}. Завершение работы...", flush=True)

    # Устанавливаем событие завершения
    shutdown_event.set()

    # Отменяем все задачи
    for task in tasks:
        if not task.done():
            task.cancel()

    # Ждем завершения задач с таймаутом
    await asyncio.gather(*tasks, return_exceptions=True)

    # Закрываем соединения с БД
    try:
        if hasattr(db, 'close'):
            db.close()
    except Exception as e:
        print(f"[ERROR] Ошибка при закрытии БД: {e}", flush=True)

    print("[INFO] Программа завершена", flush=True)


async def main():
    print("[INFO] Запуск функции main()", flush=True)

    # Настраиваем обработчики сигналов
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s.name))
        )

    # Запускаем бота и основной цикл ПАРАЛЛЕЛЬНО
    bot_task = asyncio.create_task(start_bot())
    loop_task = asyncio.create_task(main_loop())

    tasks.extend([bot_task, loop_task])

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        print("[INFO] main(): задачи отменены", flush=True)
    finally:
        if not shutdown_event.is_set():
            await shutdown("manual")


if __name__ == "__main__":
    init()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Программа прервана пользователем", flush=True)
    except Exception as e:
        print(f"[ERROR] Критическая ошибка: {e}", flush=True)
        sys.exit(1)