import pandas as pd
from connection import alor_client


import pandas as pd
from connection import alor_client


def fetch_trades_data(exchange, symbol, seconds_from, seconds_to):
    all_data = []

    while seconds_from < seconds_to:
        data = alor_client.get_all_trades(
            exchange=exchange,
            symbol=symbol,
            seconds_from=seconds_from,
            seconds_to=seconds_to,
            take=1000000,
            format='Simple',
        )
        print("Полученные данные:", data)  # Выводим полученные данные
        print(f"Количество сделок: {len(data)}")

        if not data or len(data) == 0:
            print("Нет данных для обработки.")
            break

        last_trade_time = max([trade['timestamp'] for trade in data])  # Максимальный timestamp
        print(f'last_trade_time = {last_trade_time}')

        all_data.extend(data)

        # Обновляем seconds_from на timestamp последнего трейда
        seconds_from = int(last_trade_time / 1000)

    print("all_data")
    print(all_data)
    # Собираем все данные в DataFrame
    df = pd.DataFrame(all_data)
    df = df.drop(columns=['id', 'board', "orderno", 'oi', 'existing'])
    return df


# Пример вызова функции
exchange = 'MOEX'
symbol = "USDRUBF"
seconds_from = 1734328800
seconds_to = 1734352200
df = fetch_trades_data(exchange, symbol, seconds_from, seconds_to)
print(df)

weighted_avg_price = round(((df['qty'] * df['price']).sum() / df['qty'].sum()), 6)
print(f"weighted_avg_price = {weighted_avg_price}")


