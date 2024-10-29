import connection


class Config:

    # Подключение к PostgreSQL
    postgres_connection = {
        'host': connection.postgres_host,
        'dbname': connection.postgres_dbname,
        'user': connection.postgres_user,
        'password': connection.postgres_password,
        'port': connection.postgres_port
    }

    request_metadata_period = 3600  # частота запроса метаданных в секундах
    time_window = 15 * 60  # период для расчёта временного окна
    trades_data_storage_time = 24 * 60 * 60

    min_vol_usd = 1000  # Минимальный объём, ниже которого инструменты не рассматриваются
    min_count_trades = 30
