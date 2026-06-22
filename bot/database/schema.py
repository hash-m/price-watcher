import sys
import sqlite3

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import DB_PATH


DB_CONNECTION = sqlite3.connect(DB_PATH)
cursor = DB_CONNECTION.cursor()

def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY,
            url         TEXT NOT NULL UNIQUE,
            selector    TEXT,
            channel_id  TEXT NOT NULL,
            user_id     TEXT NOT NULL,
            last_polled TIMESTAMP,
            available   BOOLEAN
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id          INTEGER PRIMARY KEY,
            product_id  INTEGER REFERENCES products(id),
            price       REAL NOT NULL,
            currency    TEXT NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY,
            product_id INTEGER REFERENCES products(id),
            user_id    TEXT NOT NULL,
            condition  TEXT NOT NULL,
            triggered  BOOLEAN DEFAULT FALSE
        )
    """)
    DB_CONNECTION.commit()

create_tables()