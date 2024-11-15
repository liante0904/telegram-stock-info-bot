import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.SQLiteManager import SQLiteManager

db = SQLiteManager()
db.open_connection()
r = db.execute_query("select * from data_main_daily_send")
print(r)
