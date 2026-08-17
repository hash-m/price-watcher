import time
import aiohttp
import base64
import logging

from bot.config import EBAY_CLIENT_ID,EBAY_CLIENT_SECRET

logger = logging.getLogger(__name__)

class EbayTokenManager():
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance            = super().__new__(cls)
            cls._instance.key        = None
            cls._instance.expiration = 0
        return cls._instance


    async def get_key(self):
        if not self.is_key_valid():
            await self.request_key()
        return self.key

    async def request_key(self):
        credentials = base64.b64encode(f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()).decode()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.ebay.com/identity/v1/oauth2/token",
                headers = {'Content-Type'  : "application/x-www-form-urlencoded", 
                            'Authorization' : f"Basic {credentials}"},
                data ={'grant_type' : "client_credentials",
                        'scope'      : "https://api.ebay.com/oauth/api_scope"}) as response:
                    response.raise_for_status()
                    data = await response.json()

            self.key = data["access_token"]
            self.expiration = data["expires_in"] + time.time()
        except aiohttp.ClientResponseError as e:
            logger.exception(f"Failed to get ebay oauth token: {e}")

    def is_key_valid(self):
        return self.key is not None and time.time() < self.expiration