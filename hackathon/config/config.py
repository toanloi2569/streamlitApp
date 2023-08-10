import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print(BASEDIR)
load_dotenv(os.path.join(BASEDIR, '.env'), override=True)

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
DATABASE = os.getenv('DATABASE')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
SCHEMA = os.getenv('SCHEMA')

print(HOST)
print(PORT)
print(DATABASE)
print(USER)
print(PASSWORD)
print(SCHEMA)
