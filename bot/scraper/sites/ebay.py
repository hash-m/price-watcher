from bot.scraper.fetcher          import fetch_json
from bot.exceptions               import ExtractionError,FetchingError
from bot.database.queries         import get_init_price
from urllib.parse                 import urlparse
from bot.access_tokens.ebay_token import EbayTokenManager

def get_itemid(url):
    if isinstance(url,str):
        try:
            path = urlparse(url).path
            return int(path.strip('/').split("/")[1])
        except (ValueError,IndexError):
            return None

async def fetch(url):
    item_id = get_itemid(url)

    if item_id is None:
        raise FetchingError("ebay",url,"Invalid URL (Can't find itemid)")

    manager = EbayTokenManager()
    key = await manager.get_key()

    headers = {
        "Authorization"            : f"Bearer {key}",
        "X-EBAY-C-MARKETPLACE-ID"  : "EBAY_GB",
        "Accept-Language"          : "en-GB"
    }

    return await fetch_json(f"https://api.ebay.com/buy/browse/v1/item/v1|{item_id}|0",headers)

async def extract(json):
    if not json or "itemId" not in json:
        raise ExtractionError("ebay", "JSON not found")

    info           = {}
    availabilities = json.get("estimatedAvailabilities", [])
    availability   = availabilities[0] if availabilities else {}
    price          = json.get("price", {})

    if price is None:
        raise ExtractionError("ebay","No price available")

    info["Name"]         = json.get("title")
    info["InitialPrice"] = None
    info["FinalPrice"]   = float(price.get("value", -1))
    if info["FinalPrice"] == -1:
        raise ExtractionError("ebay", f"No price available\n{price}")
    info["Available"]    = availability.get("estimatedAvailabilityStatus") == "IN_STOCK"

    return info