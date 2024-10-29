import time

import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from Telegram_bot.send_message import TelegramSendMessage
import json


def check_last_send_time():
    pass

def get_exchange_rates():
    tg = TelegramSendMessage()
    chat_id = 503034116
    last_time_message = 0

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

        # Инициализируем переменные для хранения цен валют
        usd_rub = None
        eur_rub = None
        cny_rub = None

        # Проходим по всем валютам в XML
        for valute in root.findall('Valute'):
            code = valute.find('CharCode').text
            value = valute.find('Value').text

            if code == 'USD':
                usd_rub = value
            elif code == 'EUR':
                eur_rub = value
            elif code == 'CNY':
                cny_rub = value

        # Сравниваем date_attr_formatted и tomorrow_date
        if date_attr_formatted == tomorrow_date:
            # Возвращаем значения всех переменных
            result = {
                'Дата': date_attr_formatted,
                'USD_RUB': usd_rub,
                'EUR_RUB': eur_rub,
                'CNY_RUB': cny_rub
            }
            message = "\n".join([f"{key}: {value}" for key, value in result.items()])
            print(result, time.time())
            tg.send_text_message(message, chat_id=chat_id)
            return result
        else:
            if time.time() >= (last_time_message + 43200):
                # Возвращаем None
                result = {
                    'Дата': date_attr_formatted,
                    'USD_RUB': usd_rub,
                    'EUR_RUB': eur_rub,
                    'CNY_RUB': cny_rub
                }
                data_str = "\n".join([f"{key}: {value}" for key, value in result.items()])

                message = "[INFO] Завтрашних курсов ещё нет."
                # tg.send_text_message(message, chat_id=chat_id)
                print(message, time.time())
                # print(data_str)
                last_time_message = time.time()
                return None
            else:
                print("Сегодняшнее сообщение уже отправлено!")
                return None


    else:
        print(f'Ошибка при выполнении запроса: {response.status_code}')


if __name__ == "__main__":
    while True:
        get_exchange_rates()
        time.sleep(5)