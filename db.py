import sqlite3
import os

DB_PATH = os.getcwd()

def connect_db():
    connection = sqlite3.connect(DB_PATH + '\\movies.db')
    connection.row_factory = sqlite3.Row
    database = connection.cursor()
    create_table(database)
    return connection, database

def create_table(database):
    try:
        database.execute('''
            CREATE TABLE IF NOT EXISTS "companies" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" TEXT
            );
        ''')
        database.execute('''
            CREATE TABLE IF NOT EXISTS "venues" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "company_id" integer,
                "name" TEXT,
                "code" TEXT
            );
        ''')
        database.execute('''
            CREATE TABLE IF NOT EXISTS "venue_has_movie" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "venue_id" INTEGER,
                "movie_id" INTEGER
            );
        ''')
        database.execute('''
            CREATE TABLE IF NOT EXISTS "halls" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "venue_id" INTEGER,
                "name" TEXT,
                "code" TEXT
            );
        ''')
        database.execute('''
            CREATE TABLE IF NOT EXISTS "hall_has_movie" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "hall_id" INTEGER,
                "movie_date_id" INTEGER,
                "timeable_id" INTEGER
            );
        ''')
        database.execute('''
            CREATE TABLE IF NOT EXISTS "timeables" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" TEXT,
                "code" TEXT
            );
        ''')
        database.execute('''
            CREATE TABLE IF NOT EXISTS "movie_date" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "movie_id" INTEGER,
                "date" DATE
            );
        ''')
        database.execute('''
            CREATE TABLE IF NOT EXISTS "movies" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" TEXT,
                "name_en" TEXT,
                "release_time" DATE,
                "image" TEXT,
                "description" TEXT,
                "director" TEXT,
                "showtimes" TEXT,
                "vscinemas" TEXT
            );
        ''')
    except sqlite3.OperationalError:  # 捕捉不合法的數值輸入
        print("資料表新增失敗")

def insert(table_name, data):
    connection, database = connect_db()
    try:
        database.execute(f"INSERT INTO {table_name} (`{'`,`'.join(data.keys())}`) VALUES ({','.join(['?' for item in data])});", list(data.values()))
        connection.commit()
    except sqlite3.OperationalError as err:
        print(f"{table_name}資料表新增失敗::")
        print(err)

def update(table_name, data, id):
    connection, database = connect_db()
    try:
        set_clause = ", ".join([f"{key} = ?" for key, value in data.items()])
        database.execute(f"UPDATE {table_name} SET {set_clause} Where id = ?;", list(data.values()) + [id])
        connection.commit()
    except sqlite3.OperationalError as err:
        print(f"{table_name}資料表更新失敗::")
        print(err)

def delete(table_name, id):
    connection, database = connect_db()
    try:
        database.execute(f"DELETE FROM {table_name} Where id = ?;", [id])
        connection.commit()
    except sqlite3.OperationalError as err:
        print(f"{table_name}資料表刪除失敗::")
        print(err)