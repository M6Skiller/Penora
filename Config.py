import os
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')

result = urlparse(database_url)

if os.getenv('TOKEN') is not None:
    API_TOKEN = os.environ.get('TOKEN')
else:
    print("You don't have token for your bot ❌")

admins = [229697988]

db_name = os.environ.get('database' , 'Store')

db_config = {
    'user': result.username,
    'password': result.password,
    'host': result.hostname,
    'port': result.port,
    'database': result.path.lstrip('/')
}
