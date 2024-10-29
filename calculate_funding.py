import pandas as pd


def calculate_funding(client, symbol, cbr_price, K1, K2):
    """
    Расчитывает среднее значение отклонения цен Контракта и цен базисного актива на каждую минуту в
    течение времени проведения основной торговой сессии на Срочном рынке.

    :param symbol str: тикер актива, по которому нужен расчёт
    :param float cbr_price: цена спота валюты, рассчитываемая ЦБ на следующий день
    """

    exchange = 'MOEX'
    candles = client.get_history(exchange=exchange, symbol=symbol)

    df = pd.DataFrame(candles["history"])
    df["PQ"] = df["close"] * df["volume"]
    sum_volume = sum(df["volume"])
    sum_PQ = sum(df["PQ"])

    D = sum_PQ / sum_volume - cbr_price

    L1 = K1 * cbr_price
    L2 = K2 * cbr_price
    Funding = min(L2, max(-L2, (min(-L1, D) + max(L1, D))))
    print(f'Стоимость фандинга для {symbol} = {round(Funding, 4)} ({(round(Funding * 1000, 2))} рублей на лот)')
    print(f'D: {round(D, 3)}, L1: {round(L1, 2)}, L2: {round(L2, 2)}', end='\n\n')


def calculate_funding_quik(symbol, weighted_average_price, cbr_price, K1, K2):
    """
    Рассчитывает значения фандинга.

    :param weighted_average_price float: Средневзвешенная цена, взятая из QUIK на 15:30
    :param symbol str: тикер актива, по которому нужен расчёт
    :param float cbr_price: цена спота валюты, рассчитываемая ЦБ на следующий день
    """

    D = weighted_average_price - cbr_price

    L1 = K1 * cbr_price
    L2 = K2 * cbr_price
    Funding = min(L2, max(-L2, (min(-L1, D) + max(L1, D))))
    print(f'Стоимость фандинга для {symbol} = {round(Funding, 4)} ({(round(Funding*1000, 2))} рублей на лот)')
    print(f'D: {round(D, 3)}, L1: {round(L1, 2)}, L2: {round(L2, 2)}', end='\n\n')

    return round(Funding*1000, 2)
