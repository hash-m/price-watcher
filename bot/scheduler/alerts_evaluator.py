import aiosqlite
import discord
import logging

from bot.broadcasting.notify import send_embed_to_user
from bot.database.connection import Database

logger = logging.getLogger(__name__)

async def get_watch_from_alert(alert):
    db         = await Database().get_connection()
    product_id = alert[1]
    user_id    = alert[2]
    
    try:
        cursor = await db.execute(
            """
            SELECT * 
            FROM   watches
            WHERE  product_id = ? AND user_id = ?
            """,
            (product_id,user_id)
        )
        return await cursor.fetchone()
    except aiosqlite.OperationalError as e:
        logger.exception(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        logger.exception(f"Database error: {e}")
        return []


async def get_alerts(product_id):
    db = await Database().get_connection()
    
    try:
        return await db.execute_fetchall(
            """
            SELECT * 
            FROM   alerts
            WHERE  product_id = ?
            """,
            (product_id,)
        )
    except aiosqlite.OperationalError as e:
        logger.exception(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        logger.exception(f"Database error: {e}")
        return []


"""
    should_notify_user()
        params:
            alert   = alert tuple which is obtained from an SQL search for the user's alert
            product = the data obtained from the scraping the data from the product's website

        desc:
            this function checks the alert and its status, sending a reset flag if the new data falls behind the trigger or 
            sending a notify flag if the new data is reaches or exceeds the trigger and if the alert hasn't been triggered yet.
"""
async def should_notify_user(alert,product):
    price        = product["FinalPrice"]
    percentage   = product["Percentage"]
    availability = product["Available"]
    
    target       = alert[3]
    trigger      = alert[4]
    triggered    = alert[5]

    match target:
        case "price":
            if price is None:
                return "dont"
            elif price <= trigger and not triggered:
                return "notify"
            elif price > trigger and triggered:
                return "reset"
        case "percentage":
            if percentage is None:
                return "dont"
            elif percentage >= trigger and not triggered:
                return "notify"
            elif percentage < trigger and triggered:
                return "reset"
        case "availability":
            if availability == trigger and not triggered:
                return "notify"
            elif availability != trigger and triggered:
                return "reset"
        case _:
            raise ValueError(f"Unknown target: {target}")

    return "dont"


async def notify(alert,product):
    watch      = await get_watch_from_alert(alert)
    channel_id = watch[2]
    user_id    = watch[0]
    target     = alert[3]

    embed = discord.Embed(
            title="Product Update!",
            color=discord.Colour.green(),
        )
    
    match target:
        case "price":
            embed.description = f"[{product["Name"]}'s]({product["URL"]}) price has reduced to £{product["FinalPrice"]}!"
        case "percentage":
            embed.description = f"[{product["Name"]}]({product["URL"]}) is now {product["Percentage"]}% off!"
        case "availability":
            embed.description = f"[{product["Name"]}]({product["URL"]}) is now {'available!' if product["Available"] else 'unavailable.'}"
    
    await send_embed_to_user(channel_id,user_id,embed)


async def set_alerts_triggered_field(alert,truefalse):
    db = await Database().get_connection()
    
    try:
        await db.execute(
            """
            UPDATE alerts
            SET triggered = ?
            WHERE id = ?
            """,
            (truefalse,alert[0])
        )
        await db.commit()
    except aiosqlite.Error as e:
        await db.rollback()
        logger.exception(f"Database error: {e}")
    

async def notify_eligible_users(product,scraped_data):
    alerts = await get_alerts(product[0])

    for alert in alerts:
        should_notify = await should_notify_user(alert,scraped_data)

        match should_notify:
            case "notify":
                try:
                    await notify(alert,scraped_data)
                    await set_alerts_triggered_field(alert,True)
                except discord.DiscordException as e:
                    logger.exception(f"Failed to notify for alert {alert[0]}: {e}")
            case "reset":
                await set_alerts_triggered_field(alert,False)