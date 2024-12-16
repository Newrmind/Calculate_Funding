from Database.database import Database
from Database.create_database import CreateDatabase

db_creator = CreateDatabase()
db_creator.create_database("Funding")
db_creator.create_table_requests_time()

db = Database()