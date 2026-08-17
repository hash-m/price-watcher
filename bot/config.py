import os

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN      = os.getenv("DISCORD_TOKEN")
EBAY_CLIENT_ID     = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

POLL_INTERVAL = 1800 #30 mins


_BASE_DIR = Path(__file__).parent
_DATA_DIR = _BASE_DIR / "data"
_DATA_DIR.mkdir(exist_ok=True)
DB_PATH = _DATA_DIR / "bot.db"