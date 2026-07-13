import inspect

from urllib.parse      import urlparse
from bot.exceptions    import FetchingError,ExtractionError
from bot.scraper       import format,fetch_playwright
from bot.scraper.sites import steam,ebay,bandq


SCRAPER_MAPPING = {
    "diy.com" : {
        "extract" : bandq.extract,
        "fetch"   : fetch_playwright
    },
    "ebay.co.uk" : {
        "extract" : ebay.extract,
        "fetch"   : ebay.fetch
    },
    "store.steampowered.com" : {
        "extract" : steam.extract,
        "fetch"   : steam.fetch
    }
}
 
def get_functions(url):
    domain = urlparse(url).netloc
    domain = domain.replace("www.", "")
    return SCRAPER_MAPPING.get(domain)


"""
    call scrape for it to scrape the page and return the necessary data in a readable format.

    data = {
        [Name] = name of product
        [InitialPrice] = if product is discounted, the original price will be here
        [FinalPrice] = the current price of the product
        [Percentage] = if product is discounted, then the percentage of the discount will be here
        [Available] = availability of the product - nil = unknown
    }
"""
async def scrape(url):
    functions = get_functions(url)
    if not functions:
        raise ValueError(f"Unsupported website: {url}")
    
    try:
        fetch = functions.get("fetch")
        extract = functions.get("extract")
    except (FetchingError, ExtractionError):
        print("raise a scrape fail error for bot to catch and send a message to the user")
        return
 
    data = await fetch(url)
    
    if inspect.iscoroutinefunction(extract):
        useful_data = await extract(data)
    else:
        useful_data = extract(data)    

    useful_data = format(useful_data)
    return useful_data