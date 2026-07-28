import aiosqlite

from bot.database.connection import Database
from bot.database.queries import get_product

async def alert_exists(url,user_id,target):
    db = await Database().get_connection()
    
    try:
        product = await get_product(url)
        product_id = product[0]

        async with db.execute("SELECT * FROM alerts WHERE product_id = ? AND user_id = ? AND target = ?",(product_id,user_id,target)) as cursor:
            return await cursor.fetchone()
    except IndexError as e:
        print(f"[logic/alerts.py] Index Error: {e}")
        raise
    except aiosqlite.Error as e:
        print(f"[logic/alerts.py] Database error: {e}")
        raise

async def add_alert_to_db(url,user_id,target,trigger):
    db = await Database().get_connection()

    try:
        product = await get_product(url)
        product_id = product[0]

        await db.execute(
            """
            INSERT INTO alerts (product_id,user_id,target,trigger)
            VALUES (?, ?, ?, ?)
            """, 
            (product_id,user_id,target,trigger)
        )
        await db.commit()  
    except IndexError as e:
        print(f"[logic/alerts.py] Index Error: {e}")
        raise
    except aiosqlite.IntegrityError:
        print("[logic/alerts.py] Database error: Alert already exists")
        raise
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/alerts.py] Database error: {e}")
        raise

async def update_alert_in_db(url,user_id,target,trigger):
    db = await Database().get_connection()

    try:
        product = await get_product(url)
        product_id = product[0]

        await db.execute(
            """
            UPDATE alerts 
            SET trigger = ?, triggered = FALSE
            WHERE product_id = ? AND user_id = ? AND target = ?
            """, 
            (trigger,product_id,user_id,target)
        )
        await db.commit()  
    except IndexError as e:
        print(f"[logic/alerts.py] Index Error: {e}")
        raise
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/alerts.py] Database error: {e}\nAlert not updated")
        raise

async def remove_alert_in_db(url,user_id,target):
    db = await Database().get_connection()

    try:
        product = await get_product(url)
        product_id = product[0]

        cursor = await db.execute(
            """
            DELETE FROM alerts
            WHERE product_id = ? AND target = ? AND user_id = ?
            """, 
            (product_id,target,user_id)
        )
        await db.commit()

        if cursor.rowcount > 0:
            return "Successfully Removed"
        else:
            return "Not Found"
    except IndexError as e:
        print(f"[logic/alerts.py] Index Error: {e}")
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"[logic/alerts.py] Database Error: {e}")

    return "Error"
    
async def add_alert(url,user_id,target,trigger):
    if target not in ("price","percentage","availability"):
        raise ValueError
    
    if target == "price" and trigger < 0:
        raise ValueError
    
    if target == "percentage" and (trigger < 1 or trigger > 100):
        raise ValueError

    try:
        if await alert_exists(url,user_id,target):
            await update_alert_in_db(url,user_id,target,trigger)
            return "Updated Alert"
        else:
            await add_alert_to_db(url,user_id,target,trigger)
            return "Added Alert"
    except IndexError:
        print(f"[logic/alerts.py] Index Error: {e}")
    except aiosqlite.Error as e:
        print(f"[logic/alerts.py] Database Error: {e}")

    return "Error"
    
async def remove_alert(url,user_id,target):
    if target not in ("price","percentage","availability"):
        raise ValueError
    
    return await remove_alert_in_db(url,user_id,target)