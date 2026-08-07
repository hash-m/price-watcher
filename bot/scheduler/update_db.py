import random
import asyncio
import aiosqlite
import time

from bot.database.connection import Database
from bot.database.queries    import get_snapshots,get_init_price
from bot.config              import POLL_INTERVAL

async def update_product(product_tuple,scraped_data,poll_interval=POLL_INTERVAL):
    db         = await Database().get_connection()
    jitter     = int(poll_interval * 0.2)
    poll_time  = time.time() + poll_interval
    poll_time += random.randint(-jitter,jitter)
    poll_time  = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(poll_time))
    product_id = product_tuple[0]

    result = await get_init_price(product_id)
    init_price = result[0] if result else None
    
    #some websites (eg. ebay) don't have an initial price so we will use final price for the first time. 
    #not ideal due to certain scenarios.
    new_init_price = scraped_data["InitialPrice"] or scraped_data["FinalPrice"]

    if init_price is None or init_price < new_init_price:
        init_price = new_init_price

    product_name = scraped_data["Name"]
    available    = scraped_data["Available"]

    for attempt in range(5):
        try:
            await db.execute("UPDATE products SET next_poll = ?, name = ?, init_price = ?, available = ? WHERE id = ?", (poll_time, product_name, init_price, available, product_id))
            await db.commit()
            return
        except aiosqlite.OperationalError as e:
            if "locked" in str(e).lower() and attempt < 4:
                await asyncio.sleep(0.1 * (2 ** attempt)) #retry w/ exponential time
                continue
            raise 
        except aiosqlite.Error as e:
            print(f"Database error in update_product: {e}")
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
    
    db = await Database().get_connection()

    try:
        await db.execute("INSERT INTO product_changes(product_id,price) VALUES (?,?)",
                         (product_id,product_data["FinalPrice"])
                        )
        await db.commit()
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"Database error: {e}\n new snapshot not added")
