import asyncio
from sqlalchemy import text
from src.database.db import sessionmanager

async def test_connection():
    async with sessionmanager.session() as session:
        result = await session.execute(text("SELECT 1"))
        print("Connection successful:", result.scalar())

if __name__ == "__main__":
    asyncio.run(test_connection())
