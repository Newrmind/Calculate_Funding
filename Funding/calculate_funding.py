from config import Config
from Funding.moex_data_request import get_prevsettlerprice
from Funding.weighted_average_price import weighted_avg_price

def calculate_funding(symbol, cbr_prices, K1=None, K2=None, previous_price=None, weighted_average_price=None):
    """
    Расчитывает среднее значение отклонения цен Контракта и цен базисного актива на каждую минуту в
    течение времени проведения основной торговой сессии на Срочном рынке.

    :param symbol str: тикер актива, по которому нужен расчёт
    :param float previous_price: расчетная цена по вечному фьючерсу за предыдущий вечерний клиринг
    :param float weighted_average_price: средневзвешенная цена по вечному фьючерсу на 15:30
    :param float cbr_price: цена спота валюты, рассчитываемая ЦБ на следующий день
    """

    if not previous_price:
        previous_price = get_prevsettlerprice()[symbol]
    if not weighted_average_price:
        weighted_average_price = weighted_avg_price(symbol=symbol)
    if not K1:
        K1 = Config.futures_params[symbol][1]
    if not K2:
        K2 = Config.futures_params[symbol][2]

    if previous_price and weighted_average_price:
        spot_symbol = Config.futures_params[symbol][0]
        cbr_price = float(cbr_prices[spot_symbol].replace(',', '.'))

        D = weighted_average_price - cbr_price

        L1 = K1 * previous_price
        L2 = K2 * previous_price
        Funding = min(L2, max(-L2, (min(-L1, D) + max(L1, D))))
        funding_message = (f'Фандинг по {symbol}: {round(Funding, 4)} ({(round(Funding*1000, 2))} рублей на лот.\n'
                           f'Средневзвешенная цена: {round(weighted_average_price, 6)})')
        print("funding_message", funding_message)
        return funding_message
    else:
        return None


if __name__ == "__main__":
    tickers = ['USDRUBF', "EURRUBF"]
    cbr_prices = {'Дата': '17/12/2024', 'USD_RUB': '102,9125', 'EUR_RUB': '108,7016'}
    for ticker in tickers:
        calculate_funding(symbol=ticker, cbr_prices=cbr_prices)




