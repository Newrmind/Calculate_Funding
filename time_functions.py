from datetime import datetime, timedelta, timezone
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


def request_time_change(db, request: str, reset_time: bool = False):
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
        if not reset_time:
            requests_time.loc[requests_time['request'] == request, 'time_msk'] = time_msk
            requests_time.loc[requests_time['request'] == request, 'timestamp'] = timestamp
        else:
            requests_time.loc[requests_time['request'] == request, 'time_msk'] = "00-00-0000 00:00:00 - Empty"
            requests_time.loc[requests_time['request'] == request, 'timestamp'] = 0
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
    print(f"[INFO] Текущая дата и время по МСК: {now.strftime('%d-%m-%Y %H:%M:%S')} - {now.strftime('%A')}")

    # Проверка времени и дня недели
    if now.weekday() < 5 and (now.hour == 15 and now.minute >= 30 or
                              (now.hour > 15 and now.hour < 23) or
                              (now.hour == 23 and now.minute <= 45)):
        return True
    return False


def is_avg_price_check_time():
    # Устанавливаем московскую временную зону
    msk_timezone = pytz.timezone('Europe/Moscow')
    current_time_msk = datetime.now(msk_timezone)

    # Проверяем, будний ли день (0-4 = Пн-Пт, 5-6 = Сб-Вс)
    if current_time_msk.weekday() >= 5:
        return False

    # Получаем текущее время в MSK
    current_time = current_time_msk.time()

    # Задаем границы времени (10:00 и 23:30)
    start_time = datetime.strptime("10:00", "%H:%M").time()
    end_time = datetime.strptime("23:30", "%H:%M").time()

    # Проверяем, входит ли текущее время в интервал
    return start_time <= current_time <= end_time


def get_timestamps_for_funding():
    """
    Возвращает временные метки для расчёта фандинга в секундах.
    Пример: (1745391600, 1745411400)
    """
    # Указываем часовой пояс для Москвы
    moscow_tz = pytz.timezone('Europe/Moscow')

    # Получаем текущее время в Московском часовом поясе
    now = datetime.now(moscow_tz)

    # Начало текущего дня в Московском времени
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Временные метки для 9:00 и 15:30
    timestamp_10am = int((today + timedelta(hours=10)).timestamp())
    timestamp_330pm = int((today + timedelta(hours=15, minutes=30)).timestamp())

    return timestamp_10am, timestamp_330pm


def is_time_in_range(timestamp_ms):
    """
    Функция для проверки на то, что сообщение с фандингом или валютными курсами сегодня ещё не отправлялось

    :param timestamp_ms: int
    :return: bool
    """
    # Устанавливаем московский часовой пояс
    moscow_tz = timezone(timedelta(hours=3))

    # Преобразуем timestamp в объект datetime
    timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=moscow_tz)

    # Текущая дата в московском времени
    now = datetime.now(moscow_tz)
    today_start = datetime(now.year, now.month, now.day, tzinfo=moscow_tz)

    # Проверяем, является ли текущий день выходным (суббота или воскресенье)
    if today_start.weekday() in (5, 6):  # 5 = суббота, 6 = воскресенье
        return False

    # Время 15:30 и 23:00 на текущий день
    start_time = today_start.replace(hour=15, minute=30)
    end_time = today_start.replace(hour=23, minute=0)

    # Проверяем, попадает ли время в диапазон
    return not start_time <= timestamp <= end_time

def is_time_multiple_of(minutes: int) -> bool:
    """Проверяет, кратны ли текущие минуты заданному числу."""
    if minutes <= 0:
        raise ValueError("Число минут должно быть положительным.")
    now = datetime.now()
    return now.minute % minutes == 0

def timestamp_to_time(timestamp: int) -> str:
    # МСК (UTC+3)
    msk_timezone = timezone(timedelta(hours=3))

    # Переводим timestamp в datetime с учётом МСК
    dt = datetime.fromtimestamp(timestamp, tz=msk_timezone)

    # Форматируем как DD:MM:YY HH:MM
    return dt.strftime("%d-%m-%y %H:%M")



if __name__ == "__main__":
    print(timestamp_to_time(1753714908))