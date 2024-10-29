import requests
import time
from time_functions import get_moscow_time_timestamp


class AlorAPI:

    def __init__(self, refresh_token=None):
        self.refresh_token = refresh_token
        self.oauth_server = 'https://oauth.alor.ru'  # Сервер аутентификации
        self.api_server = f'https://apidev.alor.ru'  # Сервер запросов
        self.ws_server = f'wss://api.alor.ru/ws'  # Сервер подписок и событий WebSocket

    def get_jwt_token(self):
        """
        Функция для получения нового JWT токена
        """

        retries = 5
        while retries > 0:
            try:
                url = f'{self.oauth_server}/refresh?token={self.refresh_token}'

                response = requests.post(url)
                if response.status_code == 200:
                    return response.json().get('AccessToken')
                else:
                    raise Exception('Failed to refresh token', response.text)

            except Exception as ex:
                print(f"Произошла ошибка в функции get_jwt_token: {ex}")
                time.sleep(10)
                retries -= 1

    def get_all_trades(self, exchange, symbol):
        """
        Информация о всех сделках по ценным бумагам за сегодня.
        """

        retries = 5
        while retries > 0:
            try:
                if self.refresh_token:
                    url = f'{self.api_server}/md/v2/Securities/{exchange}/{symbol}/alltrades'
                    headers = {
                        'Authorization': f'Bearer {self.get_jwt_token()}'
                    }

                    params = {"format": "Simple", "from": 1721718000, "to": 1721749200}
                    response = requests.get(url, headers=headers, params=params)
                else:
                    print("Данный запрос нельзя выполнить анонимно! Нужен jwt_token!")
                    return None

                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception('Failed to fetch trades data', response.text)

            except Exception as ex:
                print(f"Произошла ошибка в функции get_all_trades: {ex}")
                time.sleep(10)
                retries -= 1

    def get_history(self, exchange, symbol):
        """
        Запрос истории рынка для выбранных биржи и финансового инструмента.
        Данные имеют задержку в 15 минут, если запрос не авторизован. Для авторизованных клиентов задержка не применяется.
        Запрос может быть выполнен без авторизации. При отправке анонимного запроса вернутся данные, бывшие актуальными 15 минут назад.
        """

        retries = 5
        while retries > 0:
            try:

                params = {"symbol": symbol, "exchange": exchange,
                          "tf": 15, "from": get_moscow_time_timestamp("10:00"),
                          "to": get_moscow_time_timestamp("15:30"),
                          "format": "Simple"}

                if self.refresh_token:
                    url = f'{self.api_server}/md/v2/history'
                    headers = {
                        'Authorization': f'Bearer {self.get_jwt_token()}'
                    }
                    response = requests.get(url, headers=headers, params=params)

                else:
                    url = f'{self.api_server}/md/v2/history'
                    response = requests.get(url, params=params)

                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception('Failed to fetch trades data', response.text)

            except Exception as ex:
                print(f"Произошла ошибка в функции get_history: {ex}")
                time.sleep(10)
                retries -= 1




