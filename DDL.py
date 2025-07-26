import mysql.connector
from Config import config, db_name

def create_database(db_name):
    conn = mysql.connector.connection.MySQLConnection(user=config['user'], password=config['password'], host=config['host'])
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
    cur.execute(f'CREATE DATABASE IF NOT EXISTS {db_name}')
    conn.commit()
    cur.close()
    conn.close()
    print(f'✅ Database {db_name} created successfully.')

def create_product_table():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS PRODUCT (
            `ID`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            `NAME`          VARCHAR(100) NOT NULL,
            `DESCRIPTION`   VARCHAR(100),
            `PRICE`         BIGINT,
            `INV`           INT,
            `DISCOUNT`      TINYINT DEFAULT 0,
            `FILE_ID`       TEXT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Table PRODUCT created successfully.")

if __name__ == '__main__':
    create_database(db_name)
    create_product_table()