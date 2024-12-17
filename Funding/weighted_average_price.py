import pandas as pd
from connection import alor_client
from time_functions import get_timestamps_for_funding


def weighted_avg_price(symbol,exchange="MOEX", seconds_from=None, seconds_to=None):
    if not seconds_from or not seconds_to:
        seconds_from, seconds_to = get_timestamps_for_funding()

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


if __name__ == "__main__":
    # Пример вызова функции
    symbol = "USDRUBF"

    seconds_from = 1734328800
    seconds_to = 1734328800
    weighted_avg_price = weighted_avg_price(symbol, seconds_from=seconds_from, seconds_to=seconds_to)

    print(f"weighted_avg_price = {weighted_avg_price}")


