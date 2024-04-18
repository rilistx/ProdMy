import random

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.querys import search_user


async def create_username(session: AsyncSession):
    while True:
        username = str(random.randint(1000000000, 9999999999))
        search = await search_user(session=session, username=username)

        if not search:
            return username
