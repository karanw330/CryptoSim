import sqlite3
import os

DB_NAME = "cryptosim.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            hashed_password TEXT,
            disabled INTEGER DEFAULT 0,
            balance_usd REAL DEFAULT 100000.0
        )
    ''')

    # Portfolio Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            symbol TEXT,
            amount REAL DEFAULT 0.0,
            FOREIGN KEY(user_id) REFERENCES users(username),
            UNIQUE(user_id, symbol)
        )
    ''')

    # Orders Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            symbol TEXT,
            order_type TEXT,
            quantity REAL,
            price REAL,
            limit_value REAL,
            stop_value REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(username)
        )
    ''')
    
    # Trades Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            quantity REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed Default User
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
