import psycopg2

from config import config
print(config.HOST, config.USER)
SCHEMA = 'public'


def get_connection():
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(
        host=config.HOST,
        database=config.DATABASE,
        user=config.USER,
        password=config.PASSWORD,
        port=config.PORT
    )
    print(conn)
    cur = conn.cursor()

    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    db_version = cur.fetchone()
    print(db_version)

    return conn


postgres_conn = get_connection()
