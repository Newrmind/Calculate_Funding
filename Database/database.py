import time
import psycopg2
import psycopg2.extras
import sqlalchemy as sa
from config import Config
import pandas as pd
from typing import Literal


class Database:
    def __init__(self, db_info: Config = Config.postgres_connection):

        self.db_info = db_info

        self.engine = sa.create_engine(
            f"postgresql+psycopg2://{self.db_info['user']}:{self.db_info['password']}@{self.db_info['host']}:"
            f"{self.db_info['port']}/{self.db_info['dbname']}")

    def connect_to_database(self):
        pg_conn = psycopg2.connect(
            host=self.db_info['host'],
            user=self.db_info['user'],
            password=self.db_info['password'],
            database=self.db_info['dbname']
        )
        return pg_conn

    # Функция получения таблицы из БД
    def get_table_from_db(self, query: str, params: tuple = ()):
        connection = self.engine.connect()
        if connection:
            try:
                df = pd.read_sql(query, connection, params=params)
                return df
            except Exception as e:
                print(f"Error executing query: {e}")
            finally:
                connection.close()
        return None

    def add_table_to_db(self, df: pd.DataFrame, table_name: str, if_exists: Literal['append', 'replace']) -> None:
        connection = self.engine.connect()
        if connection:
            try:
                df.to_sql(name=table_name, con=connection, if_exists=if_exists, index=False)
            except Exception as e:
                print(f"Error executing query: {e}")
            finally:
                connection.close()

    def change_table(self, query: str) -> None:

        connection = self.engine.raw_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()
            except Exception as e:
                print(f"Error executing query: {e}")
            finally:
                connection.close()

    def drop_table(self, table_name):
        conn = self.connect_to_database()
        cur = conn.cursor()

        try:
            drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
            cur.execute(drop_table_query)

            conn.commit()
            print(f"Table {table_name} dropped successfully.")

        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def drop_table(self, table_name):
        conn = self.connect_to_database()
        cur = conn.cursor()

        try:
            drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
            cur.execute(drop_table_query)

            conn.commit()
            print(f"Table {table_name} dropped successfully.")

        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def add_user(self, user_id, username):
        connection = self.engine.raw_connection()
        cur = connection.cursor()

        try:
            cursor = connection.cursor()
            cursor.execute("""
                            INSERT INTO users (user_id, username, created_date, created_time)
                            VALUES (%s, %s, CURRENT_DATE, CURRENT_TIMESTAMP)
                            ON CONFLICT (user_id) DO NOTHING
                            """, (user_id, username))
            connection.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            connection.close()

    def get_all_users(self):
        connection = self.engine.raw_connection()
        cur = connection.cursor()

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT user_id FROM users")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            connection.close()

    def delete_user(self, user_id):
        connection = self.engine.raw_connection()
        cur = connection.cursor()

        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            connection.commit()
            print(f"User {user_id} deleted successfully.")  # Подтверждаем удаление
        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            connection.close()


if __name__ == "__main__":
    db = Database()
    # db.drop_table('users')
    # db.create_table_order_book()
    # db.insert_data_to_orderbook(data)
    # df = db.get_table_from_db("SELECT * FROM requests_time")
    # db.add_user(123456, "test")
    # db.delete_user(user_id=123456)
