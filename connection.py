# from AlorPy.alor_api import AlorAPI
from AlorPy.AlorPy import AlorPy
from dotenv import load_dotenv
import os


load_dotenv()

refresh_token = os.getenv('refresh_token')

postgres_host = os.getenv('postgres_host')
postgres_user = os.getenv('postgres_user')
postgres_password = os.getenv('postgres_password')
postgres_dbname = os.getenv('postgres_dbname')
postgres_port = os.getenv('postgres_port')

bot_token = os.getenv('bot_token')
tg_admin_id = int(os.getenv('tg_admin_id'))

alor_client = AlorPy(refresh_token=refresh_token)

# client = AlorAPI(refresh_token=refresh_token)