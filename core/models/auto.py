from sqlalchemy.ext.asyncio import AsyncSession

from core.commands.creator import creator
from core.models.models import Base, Language, Currency, Country, Region, City, Catalog, Subcatalog, User
from core.models.querys import create_username, get_language_one, get_currency_one, get_catalog_one, \
    get_subcatalog_one, get_country_one, get_region_one, get_city_one, search_user
from core.utils.settings import async_engine, session_maker


async def create_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await create_language(session, creator['language'])
        await create_currency(session, creator['currency'])
        await create_catalog(session, creator['catalog'])
        await create_subcatalog(session, creator['catalog'])
        await create_country(session, creator['country'])
        await create_region(session, creator['country'])
        await create_city(session, creator['country'])

        await create_admin(session)


async def drop_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def create_language(session: AsyncSession, data: dict) -> None:
    for key, info in data.items():
        lang = await get_language_one(session, language_abbreviation=key)
        if not lang:
            session.add(Language(abbreviation=key, title=info['title'], flag=info['flag']))

    await session.commit()


async def create_currency(session: AsyncSession, data: list) -> None:
    for abbreviation in data:
        currency = await get_currency_one(session, abbreviation)
        if not currency:
            session.add(Currency(abbreviation=abbreviation))

    await session.commit()


async def create_catalog(session: AsyncSession, data: dict) -> None:
    for title, info in data.items():
        catalog = await get_catalog_one(session, catalog_title=title)
        if not catalog:
            session.add(Catalog(title=title, logo=info['logo']))

    await session.commit()


async def create_subcatalog(session: AsyncSession, data: dict) -> None:
    for title, info in data.items():
        catalog = await get_catalog_one(session=session, catalog_title=title)
        for subtitle in info['sub']:
            subcatalog = await get_subcatalog_one(session, subtitle, catalog.id)
            if not subcatalog:
                session.add(Subcatalog(title=subtitle, catalog_id=catalog.id))

    await session.commit()


async def create_country(session: AsyncSession, data: dict) -> None:
    for name, info in data.items():
        country = await get_country_one(session, country_name=name)
        if not country:
            session.add(Country(name=name, flag=info['flag']))

    await session.commit()


async def create_region(session: AsyncSession, data: dict) -> None:
    for country_name, info in data.items():
        country = await get_country_one(session, country_name=country_name)
        for region_name, _ in info['region'].items():
            region = await get_region_one(session, region_name=region_name)
            if not region:
                session.add(Region(name=region_name, country_id=country.id))

    await session.commit()


async def create_city(session: AsyncSession, data: dict) -> None:
    for country_name, info in data.items():
        for region_name, city_name in info['region'].items():
            region = await get_region_one(session, region_name=region_name)
            for name in city_name:
                city = await get_city_one(session, name, region.id)
                if not city:
                    session.add(City(name=name, region_id=region.id))

    await session.commit()


async def create_admin(session: AsyncSession) -> None:
    user_exist = await search_user(session, user_id=406105379)
    if not user_exist:
        language = await get_language_one(session, language_abbreviation='uk')
        country = await get_country_one(session, country_name='uk')

        session.add(User(
            id=406105379,
            username=await create_username(session),
            first_name='admin',
            phone_number='380730797933',
            is_admin=True,
            language_id=language.id,
            country_id=country.id,
        ))

    await session.commit()
