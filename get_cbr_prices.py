import time
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET



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
                        usd_rub = value
                    elif code == 'EUR':
                        eur_rub = value

                # Сравниваем date_attr_formatted и tomorrow_date
                if date_attr_formatted == tomorrow_date:
                    # Возвращаем значения всех переменных
                    result = {
                        'Курсы ЦБ на': date_attr_formatted,
                        'USD_RUB': usd_rub,
                        'EUR_RUB': eur_rub
                    }

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
