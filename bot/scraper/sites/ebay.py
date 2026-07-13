from bot.scraper.fetcher import fetch_json
from bot.exceptions      import ExtractionError
from urllib.parse        import urlparse
from bot.config          import EBAY_TOKEN

def get_itemid(url):
    if isinstance(url,str):
        try:
            path = urlparse(url).path
            return int(path.strip('/').split("/")[1])
        except (ValueError,IndexError):
            return None

async def fetch(url):
    item_id = get_itemid(url)

    headers = {
        "Authorization"            : f"Bearer {EBAY_TOKEN}",
        "X-EBAY-C-MARKETPLACE-ID"  : "EBAY_GB",
        "Accept-Language"          : "en-GB"
    }

    return await fetch_json(f"https://api.ebay.com/buy/browse/v1/item/v1|{item_id}|0",headers)

def extract(json):
    if not json or "itemId" not in json:
        raise ExtractionError("ebay", "JSON not found")

    info           = {}
    availabilities = json.get("estimatedAvailabilities", [])
    availability   = availabilities[0] if availabilities else {}
    price          = json.get("price")


    info["Name"]       = json.get("title")
    info["FinalPrice"] = float(price.get("value", 0))
    info["Available"]  = availability.get("estimatedAvailabilityStatus") == "IN_STOCK"

    return info