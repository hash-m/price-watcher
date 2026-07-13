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
            SELECT * FROM products
            WHERE user_id = ?
            """,
            (user_id,)
        )
    except aiosqlite.OperationalError as e:
        print(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return []
    
async def get_product(url,user_id):
    db = await Database().get_connection()
    
    try:
        async with db.execute("SELECT * FROM products WHERE user_id = ? AND url = ?", (user_id,url)) as cursor:
            return await cursor.fetchone()
    except aiosqlite.OperationalError as e:
        print(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return []