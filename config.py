from dotenv import load_dotenv
from os import getenv

load_dotenv()
token = getenv('TOKEN')

URL = 'http://localhost:1234/v1/chat/completions'
HEADERS = {"Content-Type": "application/json"}

DB_NAME = 'sqlite3.db'
