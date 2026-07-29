import aiosqlite
import discord

from bot.database.connection import Database

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
        print(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
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
        print(f"Failed to fetch products to poll: {e}")
        return []
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return []


"""
    check_alert()
        params:
            alert   = alert tuple which is obtained from an SQL search for the user's alert
            product = the data obtained from the scraping the data from the product's website

        desc:
            this function check's the alert and its status, sending a reset flag if the new data falls behind the trigger or 
            sending a notify flag if the new data is reaches or exceeds the trigger and if the alert hasn't been triggered yet.
"""
async def check_alert(alert,product):
    price        = product["FinalPrice"]
    percentage   = product["Percentage"]
    availability = product["Available"]
    
    target       = alert[3]
    trigger      = alert[4]
    triggered    = alert[5]

    match target:
        case "price":
            if price <= trigger and not triggered:
                return "notify"
            elif price > trigger and triggered:
                return "reset"
        case "percentage":
            if percentage >= trigger and not triggered:
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


async def notify(bot,alert,product):
    watch      = await get_watch_from_alert(alert)
    channel_id = watch[2]
    user_id    = watch[0]
    channel    = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
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
    
    await channel.send(content=f"<@{user_id}>", embed=embed)


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
        print(f"Database error: {e}")
    

async def notify_eligible_users(bot,product,scraped_data):
    alerts = await get_alerts(product[0])

    for alert in alerts:
        should_notify = await check_alert(alert,scraped_data)

        match should_notify:
            case "notify":
                await notify(bot,alert,scraped_data)
                await set_alerts_triggered_field(alert,True)
            case "reset":
                await set_alerts_triggered_field(alert,False)