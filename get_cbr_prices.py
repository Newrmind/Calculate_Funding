import time
import requests
from datetime import datetime, timedelta, date
import xml.etree.ElementTree as ET
from config import Config



def get_exchange_rates():
    retries = 200
    while retries > 0:
        try:

            # Получаем завтрашнюю дату
            tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')

            # Формируем URL с завтрашней датой
            url = f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={tomorrow_date}'

            # Выполняем запрос к XML-ресурсу
            response = requests.get(url)

            # Проверяем, что запрос был успешным
            if response.status_code == 200:
                # Парсим XML
                root = ET.fromstring(response.content)
                date_attr = root.attrib['Date']

                # Преобразуем date_attr в формат DD/MM/YYYY
                date_attr_formatted = datetime.strptime(date_attr, '%d.%m.%Y').strftime('%d/%m/%Y')
                print(date_attr_formatted)

                # Инициализируем переменные для хранения цен валют
                usd_rub = None
                eur_rub = None

                # Проходим по всем валютам в XML
                for valute in root.findall('Valute'):
                    code = valute.find('CharCode').text
                    value = valute.find('Value').text

                    if code == 'USD':
                        usd_rub = float(value.replace(',', '.'))
                    elif code == 'EUR':
                        eur_rub = float(value.replace(',', '.'))

                # Сравниваем date_attr_formatted и tomorrow_date
                if date_attr_formatted == tomorrow_date:
                    # Возвращаем значения всех переменных
                    result = {
                        'Курсы ЦБ на': date_attr_formatted,
                        'USD_RUB': usd_rub,
                        'EUR_RUB': eur_rub,
                        'EUR_USD': round((eur_rub / usd_rub), 4)
                    }

                    today = date.today()
                    expire_date = date(Config.EXPIRE_DATE['Y'], Config.EXPIRE_DATE['M'], Config.EXPIRE_DATE['D'])

                    if Config.CNY_RUB_FIXME and Config.USD_CNY_FIXME and today == expire_date:
                        result['CNY_RUB_FIXME'] = Config.CNY_RUB_FIXME
                        result['USD_CNY_FIXME'] = Config.USD_CNY_FIXME
                        result['USD_CNY_CROSS'] = round(result['USD_RUB'] / result['CNY_RUB_FIXME'], 4)
                    return result
                else:
                    # Возвращаем None
                    message = "[INFO] Завтрашних курсов ещё нет."
                    print(message, time.time())
                    return None

        except Exception as e:
            print(e)
            time.sleep(15)
            retries -= 1

if __name__ == "__main__":
    exchange_rates = get_exchange_rates()
    print(exchange_rates)

    while True:
        exchange_rates = get_exchange_rates()
        print(exchange_rates)
        time.sleep(5)
