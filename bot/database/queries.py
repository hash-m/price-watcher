"""
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   FOR FUNCTIONS WITH JUST PURE REUSABLE SQL QUERIES
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""

import aiosqlite

from bot.database.connection import Database


async def get_snapshots(product_id):
    db = await Database().get_connection()

    try:
        return await db.execute_fetchall(
            "SELECT * FROM product_changes WHERE product_id = ? ORDER BY captured_at ASC",
            (product_id,)
        )
    except aiosqlite.OperationalError as e:
        print(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return []
    

async def get_products(user_id):
    db = await Database().get_connection()
    
    try:
        return await db.execute_fetchall(
            """
            SELECT products.*
            FROM products
            JOIN watches
            ON products.id = watches.product_id
            WHERE watches.user_id = ?
            """,
            (user_id,)
        )
    except aiosqlite.OperationalError as e:
        print(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return []
    
async def get_product(url):
    db = await Database().get_connection()
    
    try:
        async with db.execute("SELECT * FROM products WHERE url = ?", (url,)) as cursor:
            return await cursor.fetchone()
    except aiosqlite.OperationalError as e:
        print(f"Failed to fetch products to poll: {e}")
        raise
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        raise

async def create_user_if_dont_exist(user_id):
    db = await Database().get_connection()

    await db.execute(
        """
        INSERT OR IGNORE INTO users(id)
        VALUES(?)
        """,
        (user_id,)
    )

    await db.commit()

async def get_init_price(product_id):
    db = await Database().get_connection()

    try:
        async with db.execute("SELECT init_price FROM products WHERE id = ?",(product_id,)) as cursor:
            return await cursor.fetchone()
    except aiosqlite.Error as e:
        print(f"[scheduler/update_db.py/does_init_price-exist()] Database Error: {e}")
        return None