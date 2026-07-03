
import random
import aiosqlite
import asyncio
import time
import bot.database.schema as schema

from bot.scraper import scrape
from bot.config  import POLL_INTERVAL


async def get_products_to_poll():
    db = schema.DB_CONNECTION
    
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
    db         = schema.DB_CONNECTION
    jitter     = int(poll_interval * 0.2)
    poll_time  = time.time() + poll_interval
    poll_time += random.randint(-jitter,jitter)
    poll_time  = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(poll_time))

    product_id = product_tuple[0]

    for attempt in range(5):
        try:
            print(product_id)
            await db.execute("UPDATE products SET next_poll = ? WHERE id = ?", (poll_time, product_id))
            await db.commit()
        except aiosqlite.OperationalError as e:
            if "locked" in str(e).lower() and attempt < 4:
                await asyncio.sleep(0.1 * (2 ** attempt)) #retry w/ exponential time
                continue
            raise 
        except aiosqlite.Error as e:
            print(f"Database error: {e}")
            print("product poll error")
            raise


def upload_price():
    return

def check_for_alerts():
    return

async def start_polling(stop_event):
    db = schema.DB_CONNECTION
    while not stop_event.is_set():
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
        products = await get_products_to_poll()
        for product in products:
            url = product[1]
            try:
                data = await scrape(url)
                print(data)
                await update_product_poll(product)
            except Exception as e:
                print(e)
                continue
        await asyncio.sleep(3)