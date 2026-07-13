import random
import asyncio
import aiosqlite
import time


from bot.scraper             import scrape
from bot.database.connection import Database
from bot.database.queries    import get_snapshots
from bot.config              import POLL_INTERVAL

async def get_products_to_poll():
    db = Database().get_connection()
    
    try:
        return await db.execute_fetchall(
            """
            SELECT * 
            FROM   products 
            WHERE  next_poll IS NULL 
            OR     next_poll <= datetime('now')
            """
        )
    except aiosqlite.OperationalError as e:
        print(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return []

async def update_product_poll(product_tuple,poll_interval=POLL_INTERVAL):
    db         = Database().get_connection()
    jitter     = int(poll_interval * 0.2)
    poll_time  = time.time() + poll_interval
    poll_time += random.randint(-jitter,jitter)
    poll_time  = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(poll_time))

    product_id = product_tuple[0]

    for attempt in range(5):
        try:
            await db.execute("UPDATE products SET next_poll = ? WHERE id = ?", (poll_time, product_id))
            await db.commit()
            return
        except aiosqlite.OperationalError as e:
            if "locked" in str(e).lower() and attempt < 4:
                await asyncio.sleep(0.1 * (2 ** attempt)) #retry w/ exponential time
                continue
            raise 
        except aiosqlite.Error as e:
            print(f"Database error: {e}")
            print("product poll error")
            raise


def is_different_snapshot(last_snapshot,new_snapshot):
    if not last_snapshot:
        return True

    return last_snapshot[2] != new_snapshot["FinalPrice"]


async def upload_price(product_id,product_data):
    snapshots = await get_snapshots(product_id)

    last_snapshot = snapshots[0] if snapshots else None

    if not is_different_snapshot(last_snapshot,product_data):
        return
    
    db = Database().get_connection()

    try:
        await db.execute("INSERT INTO product_changes(product_id,price) VALUES (?,?)",
                         (product_id,product_data["FinalPrice"])
                        )
        await db.commit()
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"Database error: {e}\n new snapshot not added")

def check_for_alerts():
    return

async def start_polling(stop_event):
    db = Database().get_connection()
    while not stop_event.is_set():
        products = await get_products_to_poll()
        for product in products:
            url = product[1]
            try:
                data = await scrape(url)
                await upload_price(product[0],data)
                await update_product_poll(product)
            except Exception as e:
                print(e)
                continue
        await asyncio.sleep(3)