import os

if os.getenv('TOKEN') is not None:
    API_TOKEN = os.environ.get('TOKEN')
else:
    print("You don't have token for your bot ❌")

admins = [229697988]

db_name = os.environ.get('database' , 'Store')

config = {
    'user' : os.environ.get('user' , 'root'),
    'password' : os.environ.get('password' , 'password'),
    'host' : os.environ.get('host' , 'localhost'),
    'database' : db_name
}