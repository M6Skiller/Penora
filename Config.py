import os
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("DATABASE_URL is not set!")
    raise ValueError("DATABASE_URL is required but not set.")

result = urlparse(database_url)

# اگر result.path بایت است، decode کن، اگر str هست مستقیم استفاده کن
if isinstance(result.path, bytes):
    db_name = result.path.decode('utf-8').lstrip('/')
else:
    db_name = result.path.lstrip('/')

db_config = {
    'user': result.username,
    'password': result.password,
    'host': result.hostname,
    'port': result.port,
    'database': db_name
}

admins = [229697988]
