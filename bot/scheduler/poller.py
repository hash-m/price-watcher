import asyncio
import aiosqlite

from bot.scraper             import scrape
from bot.database.connection import Database
from .update_db              import update_product,upload_price
from .notifier               import notify_eligible_users

async def get_products_to_poll():
    db = await Database().get_connection()
    
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


async def start_polling(stop_event,bot):
    while not stop_event.is_set():
        products = await get_products_to_poll()
        for product in products:
            url = product[2]
            try:
                data = await scrape(url)
                await upload_price(product[0],data)
                await update_product(product,data)
                await notify_eligible_users(bot,product,data)
            except Exception as e:
                print(e)
                continue
        await asyncio.sleep(3)