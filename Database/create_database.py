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

        # Соединяемся с сервером PostgreSQL
        try:

            conn = self.connect_to_database(dbname='postgres')
            conn.autocommit = True  # Включаем autocommit для создания базы данных

            # Создаем курсор для выполнения команд
            cur = conn.cursor()

            # Создаем запрос на создание базы данных
            create_db_query = sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0").format(
                sql.Identifier(dbname)
            )

            # Выполняем запрос на создание базы данных
            cur.execute(create_db_query)

            print(f"Database {dbname} created successfully.")

        except Exception as e:
            print(f"Error creating Database {dbname}: {e}")

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
            print("Table created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


if __name__ == "__main__":
    db = CreateDatabase()
    db.create_database("funding")
    db.create_table_requests_time()



