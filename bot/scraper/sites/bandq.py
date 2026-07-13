from bot.exceptions      import ExtractionError
from bs4                 import BeautifulSoup
from bot.scraper.fetcher import fetch_json

def get_productcode(soup):
    th = soup.find("th", string="Product code")
    product_code = None
    
    if th:
        td = th.find_next_sibling("td")
        product_code = td.get_text(strip=True)

    return product_code

async def extract(html):
    soup = BeautifulSoup(html, "html.parser")
    
    was_price = soup.select_one("[data-testid='was-price']")
    price     = soup.select_one("[data-testid='product-price']")
    name      = soup.select_one("[data-testid='product-name']")
    
    product_code = get_productcode(soup)
    if not product_code:
        assert ExtractionError("bandq","Can't find product code within HTML")

    json = await fetch_json(f'https://www.diy.com/browse-mfe/api/fulfilment-options?compositeOfferId={product_code}')
    attributes = json.get("data")[0].get("attributes")
    available = False

    for key in attributes:
        items = attributes.get(key)
        
        if not isinstance(items,dict):
            continue

        available = (items.get("availability") or "") == "Available"

        if available:
            break


    return {
        "Name"         : name.text.strip(),
        "InitialPrice" : was_price.find("s").get_text(strip=True) if was_price else None,
        "FinalPrice"   : price.text.strip(),
        "Available"    : available
    }