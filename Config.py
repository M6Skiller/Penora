import os
from urllib.parse import urlparse

API_TOKEN = os.getenv('TOKEN')
if API_TOKEN is None:
    print("You don't have token for your bot ❌")

database_url = os.getenv('Database_id')
if database_url is None:
    print("DATABASE_URL is not set!")

result = urlparse(database_url)

db_config = {
    'user': result.username,
    'password': result.password,
    'host': result.hostname,
    'port': result.port,
    'database': result.path.lstrip('/')
}

admins = [229697988]
