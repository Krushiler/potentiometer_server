import sqlite3 as sql


def initialize_storage(filename: str):
    conn = sql.connect(filename, check_same_thread=False)

    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    active_config INTEGER,
                    mac_address TEXT NOT NULL,
                    user_id INTEGER NOT NULL
                )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS potentiometers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    device_id INTEGER NOT NULL
                )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS potentiometer_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value TEXT NOT NULL,
                    potentiometer_id INTEGER NOT NULL,
                    config_id INTEGER NOT NULL
                )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    device_id INTEGER NOT NULL
                )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT,
                    password TEXT,
                    token TEXT
                )''')

    conn.commit()
    cur.close()
    conn.close()
