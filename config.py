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

    futures_params = {"USDRUBF": ["USD_RUB", 0.001, 0.0015], "EURRUBF": ["EUR_RUB", 0.001, 0.0015]}  # {"Тикер": ["Тикер_спота", K1, K2]}

    CNY_RUB_FIXME = None
    USD_CNY_FIXME = None

    EXPIRE_DATE = {'Y': 2025, 'M': 6, 'D': 19}