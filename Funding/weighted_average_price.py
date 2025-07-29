import pandas as pd
from connection import alor_client
from time_functions import get_timestamps_for_funding, is_avg_price_check_time, is_time_multiple_of
import time
from Funding.data_storage import data_storage


def weighted_avg_price(symbol, exchange="MOEX", seconds_from=None, seconds_to=None):
    if not seconds_from or not seconds_to:
        seconds_from, seconds_to = get_timestamps_for_funding()

    retries = 200
    while retries > 0:
        try:
            data = alor_client.get_all_trades(
                exchange=exchange,
                symbol=symbol,
                seconds_from=seconds_from,
                seconds_to=seconds_to,
                take=1000000,
                format='Simple',
            )

            # Проверяем, что данные получены и не пусты
            if not data or len(data) == 0:
                return None

            # Собираем все данные в DataFrame
            df = pd.DataFrame(data)
            # Проверяем, что DataFrame не пуст
            if df.empty:
                return None

            df = df.drop(columns=['id', 'board', "orderno", 'oi', 'existing'])
            # Проверяем, что есть ненулевые значения в колонках qty и price
            if df['qty'].sum() == 0 or df['price'].sum() == 0:
                return None

            weighted_avg_price = round(((df['qty'] * df['price']).sum() / df['qty'].sum()), 6)

            return weighted_avg_price

        except Exception as e:
            print(e)
            time.sleep(15)
            retries -= 1


def calculate_and_save_weighted_avg_price(symbols):
    """
    Пока время в диапазоне от 10:00 до 15:50 каждые 5 минут рассчитывает средневзвешенную цену.
    """

    if not is_avg_price_check_time():
        print("[INFO] Сейчас не время расчёта средневзвешенной.")
        return

    for symbol in symbols:
        need_calc_avg = False
        now = int(time.time())

        data = data_storage.get(symbol)

        if not data:
            need_calc_avg = True
        else:
            timestamp_10am, timestamp_330pm = get_timestamps_for_funding()
            if timestamp_10am < now <= timestamp_330pm + 1200 and is_time_multiple_of(5) and now - data["timestamp"] > 250:
                need_calc_avg = True

        if need_calc_avg:
            print("[INFO] Производится расчёт средневзвешенной.")
            wap = float(weighted_avg_price(symbol=symbol))
            data_storage.set({"symbol": symbol, "avg_price": wap})
            print(data_storage.get(symbol))


if __name__ == "__main__":
    symbols = ["USDRUBF", "EURRUBF", ]

    def get_avg():
        # Пример вызова функции
        # seconds_from = 1734328800
        # seconds_to = 1734328800

        for symbol in symbols:
            wap = weighted_avg_price(symbol=symbol)
            print(f"weighted_avg_price {symbol}: {wap}")

    # get_avg()

    def save_avg():
        while True:
            calculate_and_save_weighted_avg_price(symbols)
            time.sleep(1)

    save_avg()


