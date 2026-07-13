import pytest

from bot.database.connection import Database
from bot.database.schema     import create_tables

@pytest.fixture(scope="session")
async def db_setup():
    db = Database()
    db.connect(":memory:")

    await create_tables()

    yield db
    await db.close()