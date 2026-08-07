import inspect

from urllib.parse      import urlparse
from bot.exceptions    import FetchingError,ExtractionError,ScrapeError
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
    url = url.strip()
    if "//" not in url:
        url = "//" + url 
    domain = urlparse(url).netloc.lower().removeprefix("www.")
    return SCRAPER_MAPPING.get(domain)


"""
    call scrape for it to scrape the page and return the necessary data in a readable format.

    data = {
        [Name]         = name of product
        [URL]          = url of product
        [InitialPrice] = if product is discounted, the original price will be here
        [FinalPrice]   = the current price of the product
        [Percentage]   = if product is discounted, then the percentage of the discount will be here
        [Available]    = availability of the product - nil = unknown
    }
"""
async def scrape(url):
    functions = get_functions(url)
    if not functions:
        raise ValueError(f"[scraper/core.py] Unsupported website: {url}")
    
    fetch = functions.get("fetch")
    extract = functions.get("extract")

    if fetch is None or extract is None:
        raise ScrapeError(url,f"Can't find {"fetch" if fetch is None else "extract"}{" and extract" if fetch is None and extract is None else ""}.")
 
    data = await fetch(url)
    
    if inspect.iscoroutinefunction(extract):
        useful_data = await extract(data)
    else:
        useful_data = extract(data)    
    
    useful_data["URL"] = url
    useful_data = await format(useful_data)

    return useful_data