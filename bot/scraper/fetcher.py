import aiohttp

from bot.scraper.browser import new_page


async def fetch_json(url, headers= {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Locale" : "en-GB","Accept": "application/json"}):

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
                return await response.json()

async def fetch_playwright(url):
    page = await new_page()
    await page.goto(url, wait_until="domcontentloaded")
    content = await page.content()
    await page.wait_for_timeout(5000)
    await page.close()
    return content
