from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.commands.creator import creator
from core.models.models import Base, Language, Informer, Currency, Country, Region, City, Catalog, Subcatalog, User
from core.models.querys import create_username
from core.utils.settings import async_engine, session_maker


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await create_language(session, creator['language'])
        await create_informer(session, creator['informer'])
        await create_currency(session, creator['currency'])
        await create_catalog(session, creator['catalog'])
        await create_subcatalog(session, creator['catalog'])
        await create_country(session, creator['country'])
        await create_region(session, creator['country'])
        await create_city(session, creator['country'])

        await create_admin(session)


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ########################################   AUTO CREATE   ############################################### #

async def create_language(session: AsyncSession, data: dict):
    session.add_all([Language(abbreviation=key, title=info['title'], flag=info['flag']) for key, info in data.items()])

    await session.commit()


async def create_currency(session: AsyncSession, data: list):
    session.add_all([Currency(abbreviation=abbreviation) for abbreviation in data])

    await session.commit()


async def create_informer(session: AsyncSession, data: list):
    session.add_all([Informer(key=key) for key in data])
    await session.commit()


async def create_catalog(session: AsyncSession, data: dict):
    session.add_all(
        [Catalog(title=title) for title, _ in data.items()]
    )

    await session.commit()


async def create_subcatalog(session: AsyncSession, data: dict):
    for title, sub_title in data.items():
        query = await session.execute(select(Catalog).where(Catalog.title == title))
        catalog_id = query.scalar()
        session.add_all([Subcatalog(title=title, catalog_id=catalog_id.id) for title in sub_title])

    await session.commit()


async def create_country(session: AsyncSession, data: dict):
    session.add_all(
        [Country(name=name, flag=info['flag']) for name, info in data.items()]
    )

    await session.commit()


async def create_region(session: AsyncSession, data: dict):
    for name, info in data.items():
        query = await session.execute(select(Country).where(Country.name == name))
        country = query.scalar()
        session.add_all([Region(name=region, country_id=country.id) for region, _ in info['region'].items()])

    await session.commit()


async def create_city(session: AsyncSession, data: dict):
    for _, info in data.items():
        for name, city in info['region'].items():
            query_region = await session.execute(select(Region).where(Region.name == name))
            region = query_region.scalar()
            session.add_all([City(name=name, region_id=region.id) for name in city])

    await session.commit()


async def create_admin(session: AsyncSession):
    query_language = await session.execute(select(Language).where(Language.abbreviation == 'uk'))
    language_id = query_language.scalar()

    query_country = await session.execute(select(Country).where(Country.name == 'ukraine'))
    country_id = query_country.scalar()

    session.add(User(
        id=406105379,
        uuid=await create_username(session),
        username='rilistx',
        first_name='Kyrylo',
        phone_number='380730797933',
        is_admin=True,
        language_id=language_id.id,
        country_id=country_id.id,
    ))

    await session.commit()
