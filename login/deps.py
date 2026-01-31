from typing import AsyncGenerator

from login import db


async def get_session() -> AsyncGenerator:
    async with db.async_session() as session:
        yield session
