from Database.db_connection import db
from time_functions import is_time_in_range


# Проверяем, было ли отправлено сегодня сообщение с курсами ЦБ.
last_time_send_db_response = db.get_table_from_db("SELECT timestamp FROM requests_time \
                                     WHERE request = 'cbr_prices_last_send'")
if not last_time_send_db_response.empty:
    last_time_send_msg = int(last_time_send_db_response.loc[0, 'timestamp'])
else:
    last_time_send_msg = 999

last_time_send_funding = db.get_table_from_db("SELECT timestamp FROM requests_time \
                                                             WHERE request = 'funding_last_send'")

if not last_time_send_funding.empty:
    last_time_send_funding = int(last_time_send_funding.loc[0, 'timestamp'])
else:
    last_time_send_funding = 999

need_send_exchange_rates = is_time_in_range(last_time_send_msg)
need_send_funding = is_time_in_range(last_time_send_funding)

print(last_time_send_db_response)
print(last_time_send_msg)
print(last_time_send_funding)

print(f"Need send: {(need_send_exchange_rates or need_send_funding)}")











