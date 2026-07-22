from bot.config              import DB_PATH
from bot.database.connection import Database


async def init():
    db = Database()
    await db.connect(DB_PATH)

async def create_tables():
    DB_CONNECTION = await Database().get_connection()
    await DB_CONNECTION.execute("PRAGMA foreign_keys = ON")
    
    cursor = await DB_CONNECTION.cursor()
    

    #user table exists incase i add more features which are user focused (currencies,timezone,etc.)
    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY
        )
        """)

    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY,
            name        TEXT,
            url         TEXT NOT NULL UNIQUE,
            available   BOOLEAN,
            init_price  FLOAT,
            next_poll   TIMESTAMP
        )
        """)

    await cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_changes (
            id          INTEGER PRIMARY KEY,
            product_id  INTEGER NOT NULL,
            price       REAL NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(product_id)
                REFERENCES products(id)
                ON DELETE CASCADE
        )
        """)

    await cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id           INTEGER PRIMARY KEY,
            product_id   INTEGER NOT NULL,
            user_id      INTEGER NOT NULL,
            target       TEXT NOT NULL,
            trigger      REAL NOT NULL,
            triggered    BOOLEAN DEFAULT FALSE,

            UNIQUE(product_id, user_id, target),

            FOREIGN KEY(product_id)
                REFERENCES products(id)
                ON DELETE CASCADE,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
        """)

    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS watches (
            user_id     INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            channel_id  TEXT NOT NULL,

            PRIMARY KEY(user_id, product_id),

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(product_id)
                REFERENCES products(id)
                ON DELETE CASCADE
        )
    """)
    
    await DB_CONNECTION.commit()