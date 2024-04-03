import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models.models import (Language, Informer, Region, City, Catalog, Subcatalog, User, Vacancy, Country)


# ########################################   REGISTRATION   ############################################### #

async def search_user(session: AsyncSession, user_id):
    result = await session.execute(select(User).where(User.id == user_id))

    return result.scalars().one_or_none()


async def create_username(session: AsyncSession):
    while True:
        username = str(random.randint(10000000, 99999999))
        search = await session.execute(select(User).where(User.username == username))
        result = search.scalars().one_or_none()

        if not result:
            return username


async def create_user(session: AsyncSession, user_id, uuid, first_name, phone_number, language_id, country_id):
    session.add(User(
        id=user_id,
        uuid=uuid,
        first_name=first_name,
        phone_number=phone_number,
        language_id=language_id,
        country_id=country_id,
    ))

    await session.commit()


# ########################################   GET DATA   ############################################### #

async def get_language_name(session: AsyncSession, user_id):
    query_user = await session.execute(select(User).where(User.id == user_id))
    user = query_user.scalar()
    query_lang = await session.execute(select(Language).where(Language.id == user.language_id))
    language = query_lang.scalar()

    return language.name


async def get_language_id(session: AsyncSession, name):
    query = await session.execute(select(Language).where(Language.name == name))
    language = query.scalar()

    return language.id


async def get_country_id(session: AsyncSession, name):
    query = await session.execute(select(Country).where(Country.name == name))
    country = query.scalar()

    return country.id


async def get_informer(session: AsyncSession, name: str):
    query = await session.execute(select(Informer).where(Informer.name == name))
    return query.scalar()


async def get_catalog_all(session: AsyncSession):
    query = await session.execute(select(Catalog))
    return query.scalars().all()


async def get_catalog_one(session: AsyncSession, catalog_id):
    query = await session.execute(select(Catalog).where(Catalog.id == catalog_id))
    return query.scalar()


async def get_subcatalog_all(session: AsyncSession, catalog_id):
    query = await session.execute(select(Subcatalog).where(Subcatalog.catalog_id == catalog_id))
    return query.scalars().all()


async def get_vacancy_all(session: AsyncSession, subcatalog_id):
    query = await session.execute(select(Vacancy).where(Vacancy.subcatalog_id == subcatalog_id))
    return query.scalars().all()


async def get_region_all(session: AsyncSession):
    query = await session.execute(select(Region))
    return query.scalars().all()


async def get_city_all(session: AsyncSession, region_id):
    query = await session.execute(select(City).where(City.region_id == region_id))
    return query.scalars().all()
