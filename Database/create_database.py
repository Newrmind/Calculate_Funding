import psycopg2
from config import Config
from psycopg2 import sql


class CreateDatabase:

    def __init__(self, db_info: Config = Config.postgres_connection):
        self.db_info = db_info

    def connect_to_database(self, dbname: str = None):
        pg_conn = psycopg2.connect(
            host=self.db_info['host'],
            user=self.db_info['user'],
            password=self.db_info['password'],
            database=dbname if dbname else self.db_info['dbname'],
            client_encoding='UTF8'
        )
        return pg_conn

    def create_database(self, dbname: str):
        conn = None
        cur = None

        try:
            # Подключаемся к серверу PostgreSQL
            conn = self.connect_to_database(dbname='postgres')
            conn.autocommit = True
            cur = conn.cursor()

            # Проверяем, существует ли база данных
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            db_exists = cur.fetchone()

            if not db_exists:
                # Создаём базу данных, если она не существует
                create_db_query = sql.SQL(
                    "CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0"
                ).format(sql.Identifier(dbname))
                cur.execute(create_db_query)
                print(f"[INFO] База данных {dbname} успешно создана.")
            else:
                print(f"[INFO] База данных {dbname} уже существует.")

        except Exception as e:
            print(f"[ERROR] Ошибка создания базы данных {dbname}: {e}")

        finally:
            # Закрываем курсор и соединение
            if cur:
                cur.close()
            if conn:
                conn.close()

    def create_table_requests_time(self):
        conn = None
        cur = None

        query = """
        CREATE TABLE IF NOT EXISTS requests_time (
            request TEXT,
            time_msk TEXT,
            timestamp INT
        );
        """

        try:
            conn = self.connect_to_database()
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            print("[INFO] Таблица requests_time успешно создана.")
        except Exception as e:
            print(f"[ERROR] Ошибка при создании таблицы requests_time: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def create_users_table(self):
        conn = None
        cur = None

        query = """
            CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            created_date DATE DEFAULT CURRENT_DATE,
            created_time TIME DEFAULT CURRENT_TIMESTAMP
            );
        """

        try:
            conn = self.connect_to_database()
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            print("[INFO] Таблица users успешно создана.")
        except Exception as e:
            print(f"[ERROR] Ошибка при создании таблицы users: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def create_weighted_avg_price_table(self):
        conn = None
        cur = None

        query = """
                    CREATE TABLE IF NOT EXISTS weighted_avg_prices (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    created_date DATE DEFAULT CURRENT_DATE,
                    created_time TIME DEFAULT CURRENT_TIMESTAMP
                    );
                """

        try:
            conn = self.connect_to_database()
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            print("[INFO] Таблица weighted_avg_prices успешно создана.")
        except Exception as e:
            print(f"[ERROR] Ошибка при создании таблицы weighted_avg_prices: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()



if __name__ == "__main__":
    db = CreateDatabase()
    db.create_database("funding")
    db.create_table_requests_time()
    db.create_users_table()



