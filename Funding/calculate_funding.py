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
        cbr_price = cbr_prices[spot_symbol]

        D = weighted_average_price - cbr_price

        L1 = K1 * previous_price
        L2 = K2 * previous_price
        Funding = min(L2, max(-L2, (min(-L1, D) + max(L1, D))))
        funding_message = (
            f"💰 *Фандинг по {symbol}*\n"
            f"• Средневзвешенная цена: *{weighted_average_price:.6f}*\n"
            f"• Фандинг: *{Funding:.4f}* ({Funding * 1000:.2f} ₽ на лот)\n\n"
        )
        print(funding_message)
        return funding_message
    else:
        return None


if __name__ == "__main__":
    symbols = ["USDRUBF", "EURRUBF"]
    cbr_prices = {'Курсы ЦБ на': '18/06/2025', 'USD_RUB': 78.7135, 'EUR_RUB': 90.7548, 'EUR_USD': 1.15298}
    # cbr_prices = get_cbr_prices.get_exchange_rates()
    for symbol in symbols:
        msg = calculate_funding(symbol=symbol, cbr_prices=cbr_prices)



