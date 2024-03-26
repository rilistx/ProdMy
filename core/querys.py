from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import Base, User
from .settings import async_engine


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def search_user(async_session: AsyncSession, user_id):
    async with async_session as session:
        result = await session.execute(select(User).where(User.id == user_id))

    return result.scalars().one_or_none()


async def search_username(async_session: AsyncSession, username):
    async with async_session as session:
        result = await session.execute(select(User).where(User.username == username))

    return result.scalars().one_or_none()
