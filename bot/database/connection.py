import aiosqlite

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance

    async def connect(self, path):
        self.connection = await aiosqlite.connect(path)

    async def get_connection(self):
        if self.connection is None:
            raise RuntimeError("Database has not been initialised")

        return self.connection

    async def close(self):
        await self.connection.close()


db = Database()