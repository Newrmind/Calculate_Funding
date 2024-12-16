def calculate_funding_quik(symbol, previous_price, weighted_average_price, cbr_price, K1, K2):
    """
    Расчитывает среднее значение отклонения цен Контракта и цен базисного актива на каждую минуту в
    течение времени проведения основной торговой сессии на Срочном рынке.

    :param symbol str: тикер актива, по которому нужен расчёт
    :param float previous_price: расчетная цена по вечному фьючерсу за предыдущий вечерний клиринг
    :param float weighted_average_price: средневзвешенная цена по вечному фьючерсу на 15:30
    :param float cbr_price: цена спота валюты, рассчитываемая ЦБ на следующий день
    """

    D = weighted_average_price - cbr_price

    L1 = K1 * previous_price
    L2 = K2 * previous_price
    Funding = min(L2, max(-L2, (min(-L1, D) + max(L1, D))))
    print(f'Стоимость фандинга для {symbol} = {round(Funding, 4)} ({(round(Funding*1000, 2))} рублей на лот)')
    print(f'D: {round(D, 3)}, L1: {round(L1, 2)}, L2: {round(L2, 2)}', end='\n\n')