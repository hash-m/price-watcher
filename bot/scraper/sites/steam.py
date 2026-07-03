from bot.exceptions      import ExtractionError,FetchingError
from bot.scraper.fetcher import fetch_json
from urllib.parse        import urlparse

def get_gameid(data):
    if isinstance(data, dict):
        return next(iter(data))
    elif isinstance(data,str):
        path = urlparse(data).path
        return path.strip("/").split("/")[1]
    else:
        print(data)

    return None

def extract(json):
    game_id = get_gameid(json)

    if not json.get(game_id) or not json.get(game_id).get("success"):
        raise ExtractionError("steam",f"JSON not found. #### URL: https://store.steampowered.com/api/appdetails?appids={game_id}&cc=gb")
    
    data           = json.get(game_id).get("data")
    info           = {}
    price_overview = data.get("price_overview")
    release_date   = data.get("release_date")

    info["Name"]   = data.get("name")

    if release_date:
        info["Available"] = not release_date.get("coming_soon")
    
    if price_overview:
        info["InitialPrice"] = price_overview.get("initial_formatted")
        info["FinalPrice"]   = price_overview.get("final_formatted")
        info["Percentage"]   = price_overview.get("discount_percent")
    
    if data.get("is_free"):
        info["InitialPrice"] = 0
        info["FinalPrice"]   = 0
        info["Percentage"]   = 0
    
    return info

async def fetch(url):
    game_id = get_gameid(url)

    if game_id == None:
        assert FetchingError("steam",url,"Can't find game id")

    api_url = f'https://store.steampowered.com/api/appdetails?appids={game_id}&cc=gb'
    result = await fetch_json(api_url)

    return result