import pandas as pd
from connection import alor_client
from time_functions import get_timestamps_for_funding
import time


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


if __name__ == "__main__":
    # Пример вызова функции
    symbols = ["USDRUBF", "EURRUBF", ]

    # seconds_from = 1734328800
    # seconds_to = 1734328800

    for symbol in symbols:
        wap = weighted_avg_price(symbol=symbol)
        print(f"weighted_avg_price {symbol}: {wap}")


