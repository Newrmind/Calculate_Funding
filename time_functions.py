from datetime import datetime, timedelta
import pytz
import time
import pandas as pd


def get_moscow_time_timestamp(time_str):
    """
    Принимает время в формате 'HH:MM' и возвращает время в формате timestamp на текущую дату

    :param time_str:
    :return: int(timestamp)
    """
    # Получаем текущую дату в московском часовом поясе
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_date = datetime.now(moscow_tz).date()

    # Разбираем переданное время
    hours, minutes = map(int, time_str.split(':'))

    # Создаем объект datetime для переданного времени текущего дня в московском часовом поясе
    target_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hours, minutes=minutes)
    target_time = moscow_tz.localize(target_time)

    # Преобразуем в timestamp
    timestamp = target_time.timestamp()

    return int(timestamp)


def request_time_change(db, request: str):
    """Обновляет время запросов в таблице requests_time или добавляет новую строку, если запрос не найден."""

    # Получаем текущее время в Москве
    moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))

    # Форматируем время и timestamp
    time_msk = moscow_time.strftime("%d.%m.%Y %H:%M:%S")
    timestamp = int(time.time() * 1000)

    # Получаем таблицу из базы данных
    requests_time = db.get_table_from_db('SELECT * FROM requests_time')

    # Проверяем, существует ли запрос в таблице
    if request in requests_time['request'].values:
        # Обновляем время и timestamp для существующего запроса
        requests_time.loc[requests_time['request'] == request, 'time_msk'] = time_msk
        requests_time.loc[requests_time['request'] == request, 'timestamp'] = timestamp
    else:
        # Добавляем новую строку с новым запросом
        new_row = {'request': request, 'time_msk': time_msk, 'timestamp': timestamp}
        requests_time = pd.concat([requests_time, pd.DataFrame([new_row])], ignore_index=True)

    # Обновляем таблицу в базе данных
    db.add_table_to_db(requests_time, table_name='requests_time', if_exists='replace')


# Функция для проверки времени и дня недели
async def check_time():
    """
    Проверяет, что сейчас будний день, время между 15:30 и 18:45 по МСк и возвращает True при выполнении условия.
    :return: Bool
    """
    msk = pytz.timezone('Europe/Moscow')
    now = datetime.now(msk)

    # Вывод текущей даты, времени и дня недели
    print(f"Текущая дата и время по МСК: {now.strftime('%d-%m-%Y %H:%M:%S')} - {now.strftime('%A')}")

    # Проверка времени и дня недели
    if now.weekday() < 5 and (now.hour == 15 and now.minute >= 30 or
                              (now.hour > 15 and now.hour < 18) or
                              (now.hour == 18 and now.minute <= 45)):
        return True
    return False