import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import Base, User
from .settings import async_engine, session_maker


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await create_admin(session)


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ########################################   ADMIN   ############################################### #

async def create_admin(session: AsyncSession):
    session.add(User(
        id=406105379,
        username=await create_username(session),
        first_name='admin',
        phone_number='380730797933',
        is_admin=True,
    ))

    await session.commit()


# ########################################   USER   ############################################### #

async def create_user(async_session: AsyncSession, user_id, username, first_name, phone_number):
    async with async_session as session:
        async with session.begin():
            session.add(User(
                id=user_id,
                username=username,
                first_name=first_name,
                phone_number=phone_number,
            ))

        await session.commit()


async def search_user(async_session: AsyncSession, user_id):
    async with async_session as session:
        result = await session.execute(select(User).where(User.id == user_id))

    return result.scalars().one_or_none()


async def create_username(async_session: AsyncSession):
    async with async_session as session:
        while True:
            username = str(random.randint(10000000, 99999999))
            search = await session.execute(select(User).where(User.username == username))
            result = search.scalars().one_or_none()

            if not result:
                return username
