import logging
from playwright.async_api import async_playwright


PLAYWRIGHT_INSTANCE = None
BROWSER_INSTANCE    = None
CONTEXT_INSTANCE    = None

logger = logging.getLogger(__name__)

async def get_context():
    global PLAYWRIGHT_INSTANCE, BROWSER_INSTANCE, CONTEXT_INSTANCE

    if CONTEXT_INSTANCE is None:
        PLAYWRIGHT_INSTANCE = await async_playwright().start()
        BROWSER_INSTANCE    = await PLAYWRIGHT_INSTANCE.chromium.launch(headless=True)
        CONTEXT_INSTANCE    = await BROWSER_INSTANCE.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-GB",
        )
        BROWSER_INSTANCE.on("disconnected", lambda: logger.info("Browser disconnected!"))

    return CONTEXT_INSTANCE

async def new_page():
    context = await get_context()
    page    = await context.new_page()
    
    return page

async def close_browser():
    global PLAYWRIGHT_INSTANCE, BROWSER_INSTANCE, CONTEXT_INSTANCE

    logger.info("Context:", CONTEXT_INSTANCE)
    logger.info("Browser:", BROWSER_INSTANCE)

    if CONTEXT_INSTANCE:
        logger.info("Closing context...")
        await CONTEXT_INSTANCE.close()

    if BROWSER_INSTANCE:
        logger.info("Closing browser...")
        await BROWSER_INSTANCE.close()

    if PLAYWRIGHT_INSTANCE:
        logger.info("Stopping playwright...")
        await PLAYWRIGHT_INSTANCE.stop()