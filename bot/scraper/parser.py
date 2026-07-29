import aiosqlite

from bot.database.queries    import get_init_price
from bot.database.connection import Database

async def get_init(url):
    db = await Database().get_connection()
    try:
        async with db.execute("SELECT id FROM products WHERE url = ?", (url,)) as cursor:
            product_id = await cursor.fetchone()
            if product_id:
                product_id = product_id[0]
            else:
                return None
            
            result = await get_init_price(product_id)
            if result:
                return result[0]
    except aiosqlite.Error:
        return None
    
def calculate_percentage(initial,final):
    if initial is None or final is None or initial == 0:
        return 0
    
    return 100 * (1- (final/initial))
    
def format_percentage(percentage):
    if percentage is None:
        return 0.0
    
    if isinstance(percentage, (int, float)):
        return float(percentage)
    
    return float(str(percentage).strip().strip('%'))

def format_price(price):
    if price is None:
        return None
    
    if isinstance(price, (int, float)):
        return float(price)
    
    price = str(price).strip().strip('£')

    if not price:
        return None
    
    return round(float(price), 2)

async def format(raw_info):
    info = dict(raw_info)

    if "FinalPrice" in info:
        info["FinalPrice"] = format_price(info["FinalPrice"])

    if "InitialPrice" in info:
        info["InitialPrice"] = format_price(info["InitialPrice"])
    else:
        info["InitialPrice"] = await get_init(info["URL"])
        info["InitialPrice"] = format_price(info["InitialPrice"])


    if "Percentage" in info:
        info["Percentage"] = format_percentage(info["Percentage"])
    elif "InitialPrice" in info and "FinalPrice" in info:
        info["Percentage"] = calculate_percentage(info["InitialPrice"], info["FinalPrice"])
    else:
        info["Percentage"] = 0

    return info