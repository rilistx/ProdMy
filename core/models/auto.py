from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.commands.languages import json
from core.models.models import Base, Language, Informer, Currency, Country, Region, City, Catalog, Subcatalog, User
from core.models.querys import create_username
from core.utils.settings import async_engine, session_maker


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await create_language(session, json)
        await create_informer(session, json)
        await create_currency(session, json)
        await create_country(session, json)
        await create_region(session, json)
        await create_city(session, json)
        await create_catalog(session, json)
        await create_subcatalog(session, json)
        await create_admin(session)


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ########################################   AUTO CREATE   ############################################### #


async def create_language(session: AsyncSession, language: dict):
    session.add_all([Language(name=name) for name, _ in language.items()])
    await session.commit()


async def create_informer(session: AsyncSession, informer: dict):
    session.add_all([Informer(name=name) for name, _ in informer['ua']['informer'].items()])
    await session.commit()


async def create_currency(session: AsyncSession, currency: dict):
    session.add_all([Currency(name=name) for name, _ in currency['ua']['currency'].items()])
    await session.commit()


async def create_country(session: AsyncSession, country: dict):
    session.add_all([Country(name=name) for name, _ in country['ua']['country'].items()])
    await session.commit()


async def create_region(session: AsyncSession, region: dict):
    for country, info in region['ua']['country'].items():
        query = await session.execute(select(Country).where(Country.name == country))
        country_id = query.scalar()
        session.add_all([Region(name=name, country_id=country_id.id) for name, _ in info['region'].items()])

    await session.commit()


async def create_city(session: AsyncSession, city: dict):
    for country, info_country in city['ua']['country'].items():
        query_country = await session.execute(select(Country).where(Country.name == country))
        country = query_country.scalar()
        for region, info_region in city['ua']['country'][country.name]['region'].items():
            query_region = await session.execute(select(Region).where(Region.name == region))
            region_id = query_region.scalar()
            session.add_all([City(name=name, region_id=region_id.id) for name, _ in info_region['city'].items()])

    await session.commit()


async def create_catalog(session: AsyncSession, catalog: dict):
    session.add_all([Catalog(name=name) for name, _ in catalog['ua']['catalog'].items()])
    await session.commit()


async def create_subcatalog(session: AsyncSession, subcatalog: dict):
    for catalog, info in subcatalog['ua']['catalog'].items():
        query = await session.execute(select(Catalog).where(Catalog.name == catalog))
        catalog_id = query.scalar()
        session.add_all([Subcatalog(name=name, catalog_id=catalog_id.id) for name, _ in info['sub_name'].items()])

    await session.commit()


async def create_admin(session: AsyncSession):
    query_language = await session.execute(select(Language).where(Language.name == 'ua'))
    language_id = query_language.scalar()

    query_country = await session.execute(select(Country).where(Country.name == 'ua'))
    country_id = query_country.scalar()

    session.add(User(
        id=406105379,
        uuid=await create_username(session),
        username='rilistx',
        first_name='Admin',
        phone_number='380730797933',
        is_admin=True,
        language_id=language_id.id,
        country_id=country_id.id,
    ))

    await session.commit()
