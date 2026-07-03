import sys
import asyncio
import aiosqlite

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import DB_PATH

DB_CONNECTION = None

async def init():
    global DB_CONNECTION
    DB_CONNECTION = await aiosqlite.connect(DB_PATH)

async def create_tables():
    cursor = await DB_CONNECTION.cursor()
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY,
            url         TEXT NOT NULL UNIQUE,
            channel_id  TEXT NOT NULL,
            user_id     TEXT NOT NULL,
            next_poll   TIMESTAMP,
            available   BOOLEAN,
            UNIQUE(url, user_id)
        )
    """)

    await cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_changes (
            id          INTEGER PRIMARY KEY,
            product_id  INTEGER REFERENCES products(id),
            price       REAL NOT NULL,
            currency    TEXT NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    await cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY,
            product_id INTEGER REFERENCES products(id),
            user_id    TEXT NOT NULL,
            condition  TEXT NOT NULL,
            triggered  BOOLEAN DEFAULT FALSE
        )
        """)
    await DB_CONNECTION.commit()