import aiohttp

from bot.exceptions import ExtractionError
from bot.config import EBAY_TOKEN

def get_itemid():
    return None

async def fetch(url):
    item_id = get_itemid(url)

    headers = {
        "Authorization"            : f"Bearer {EBAY_TOKEN}",
        "X-EBAY-C-MARKETPLACE-ID"  : "EBAY_GB",
        "Accept-Language"          : "en-GB"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.ebay.com/buy/browse/v1/item/v1|{item_id}|0",
            headers=headers
        ) as response:
            return await response.json()

def extract(json):
    if not json or "itemId" not in json:
        raise ExtractionError("ebay", "", "JSON not found")

    info           = {}
    availabilities = json.get("estimatedAvailabilities", [])
    availability   = availabilities[0] if availabilities else {}
    price          = json.get("price")


    info["Name"]       = json.get("title")
    info["FinalPrice"] = float(price.get("value", 0))
    info["Available"]  = availability.get("estimatedAvailabilityStatus") == "IN_STOCK"

    return info