import sys
import threading
from Database.database import Database
import time_functions
from config import Config
import time
from get_cbr_prices import get_exchange_rates







def load_data(db, data_preprocessing):
    """Получить курсы валют ЦБ."""

    try:
        while True:
            last_time_request_metadata = int(db.get_table_from_db("SELECT timestamp FROM requests_time \
                                     WHERE request = 'cbr_prices_update'").loc[0, 'timestamp'])
            need_analyze = time_functions.has_passed_any_sec(timestamp=last_time_request_metadata,
                                                             seconds=Config.request_metadata_period)

            if need_analyze:
                info_message = '[INFO] Запуск функции обновления метаданных.'
                print(info_message)

                data_preprocessing.clear_and_save_exchange_info()

            else:
                data_preprocessing.clear_and_save_trades()

    except Exception as ex:
        print(f"В функции load_data произошла ошибка: {ex}")






if __name__ == "__main__":
    db = Database()
    data_preprocessing = DataPreprocessing()

    # Загрузка и подготовка данных
    thread_load_data = threading.Thread(target=load_data, name='Thread_load_data',
                                        args=(db, data_preprocessing,), daemon=True)
    thread_load_data.start()

    # Расчёты
    thread_calculation = threading.Thread(target=spread_calculation, name='Thread_calculation', daemon=True)
    thread_calculation.start()

    # Список потоков
    threads = [thread_load_data, thread_calculation]

    # Проверка запущенных потоков
    while True:
        # Получение списка активных потоков
        active_threads = threading.enumerate()
        print('\nСписок активных потоков:')
        for thread in active_threads:
            print(thread.name)

        # Проверка состояния потоков и обработка ошибок
        for thread in threads:
            if not thread.is_alive():
                message = f'Поток {thread.name} завершился с ошибкой или был прерван.'
                print(message)

        # Проверка состояния потоков и обработка ошибок
        for thread in threads:
            if not thread.is_alive():
                message = f'Поток {thread.name} завершился с ошибкой или был прерван.'
                print(message)
                sys.exit(1)

        time.sleep(15)






