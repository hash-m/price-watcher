import aiosqlite
import time

from bot.database.queries    import get_product,create_user_if_dont_exist, get_products
from bot.database.connection import Database

async def create_product(url):
    db        = await Database().get_connection()
    poll_time = time.time() + 90
    poll_time = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(poll_time))


    try:
        cursor = await db.execute(
            """
            INSERT INTO products (url,next_poll)
            VALUES (?, ?)
            """, 
            (url, poll_time)
        )
        await db.commit()  

        return cursor.lastrowid
    except aiosqlite.IntegrityError:
        print("[logic/watching.py] Already tracking this URL")
        raise
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/watching.py] Database error: {e}\nProduct entry not added")
        raise

async def create_watch(user_id,product_id,channel_id):
    db = await Database().get_connection()

    try:
        await db.execute(
            """
            INSERT INTO watches (user_id,product_id,channel_id)
            VALUES (?, ?, ?)
            """,
            (user_id,product_id,channel_id)
        )
        await db.commit()
    except aiosqlite.IntegrityError:
        print("[logic/watching.py] Already tracking this URL")
        raise
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/watching.py] Database error: {e}\nWatch not added")
        raise

async def delete_watch(user_id,product_id):
    db = await Database().get_connection()

    try:
        cursor = await db.execute(
            """
            DELETE FROM watches
            WHERE user_id = ? AND product_id = ?
            """, 
            (user_id,product_id)
        )
        await db.commit()

        if cursor.rowcount > 0:
            return "Successfully deleted product from watchlist."
        else:
            return "No product found to be deleted."
    except aiosqlite.Error as e:
        await db.rollback()
        raise

async def get_product_watches(product_id):
    db = await Database().get_connection()

    try:
        return await db.execute_fetchall(
            """
            SELECT *
            FROM watches
            WHERE product_id = ?
            """, 
            (product_id,)
        )
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/watching.py] Database Error: {e}")
        raise

async def delete_product(url):
    db = await Database().get_connection()

    try:
        await db.execute(
            """
            DELETE FROM products
            WHERE url = ?
            """, 
            (url,)
        )
        await db.commit()
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/watching.py] Database Error: {e}")
        raise

async def delete_user(user_id):
    db = await Database().get_connection()

    try:
        await db.execute(
            """
            DELETE FROM users
            WHERE id = ?
            """, 
            (user_id,)
        )
        await db.commit()
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/watching.py] Database Error: {e}")
        raise

async def watch_product(url,channel_id,user_id):

    try:
        product = await get_product(url)
        product_id = None
        if not product:
            product_id = await create_product(url)
        else:
            product_id = product[0]
        
        await create_user_if_dont_exist(user_id)    
        await create_watch(user_id,product_id,channel_id)
        return "Success"
    except aiosqlite.IntegrityError:
        return "Already Watching"
    except aiosqlite.Error as e:
        print(f"[logic/watching.py] Database Error: {e}")
        return "Error"



async def unwatch_product(url,user_id):
    try:
        product = await get_product(url)

        if not product:
            print("Product not found")
            return "Error"

        product_id = product[0]
        result = await delete_watch(user_id,product_id)

        if result == "Error":
            return result
        
        watches = await get_product_watches(product_id)

        if not watches:
            await delete_product(url)

        if not await get_products(user_id):
            await delete_user(user_id)
        
        return result
    except IndexError as e:
        print(f"[logic/watching.py] Index Error")
        return "Error" 
    except aiosqlite.Error as e:
        print(f"[logic/watching.py] Database Error: {e}")
        return "Error"