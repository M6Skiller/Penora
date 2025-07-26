import os
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')
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
