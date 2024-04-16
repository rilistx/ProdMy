import random

from sqlalchemy import select, update, delete  # noqa
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.models import Language, User, Separator, Currency, Catalog, Subcatalog, Country, Region, City, Vacancy, \
    Liked, Complaint


# ########################################   USER   ############################################### #

async def search_user(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))

    return result.scalar()


async def create_username(session: AsyncSession):
    while True:
        username = str(random.randint(10000000, 99999999))
        search = await session.execute(select(User).where(User.username == username))
        result = search.scalars().one_or_none()

        if not result:
            return username


async def create_user(session: AsyncSession, user_id, username, first_name, phone_number, language_id) -> None:
    session.add(User(
        id=user_id,
        username=username,
        first_name=first_name,
        phone_number=phone_number,
        language_id=language_id,
    ))

    await session.commit()


# ########################################   FILTER   ############################################### #

async def create_filter(session: AsyncSession, user_id, currency_id, country_id) -> None:
    session.add(Separator(
        id=user_id,
        currency_id=currency_id,
        country_id=country_id,
    ))

    await session.commit()


# ########################################   GET DATA   ############################################### #

async def get_language_all(session: AsyncSession):
    query = await session.execute(select(Language))

    return query.scalars().all()


async def get_language_one(session: AsyncSession, language_id=None, language_abbreviation=None):
    if language_id:
        query = await session.execute(select(Language).where(Language.id == language_id))
    else:
        query = await session.execute(select(Language).where(Language.abbreviation == language_abbreviation))

    return query.scalar()


async def get_catalog_all(session: AsyncSession):
    query = await session.execute(select(Catalog))

    return query.scalars().all()


async def get_catalog_one(session: AsyncSession, catalog_id=None, catalog_title=None, catalog_logo=None):
    if catalog_id:
        query = await session.execute(select(Catalog).where(Catalog.id == catalog_id))
    elif catalog_title:
        query = await session.execute(select(Catalog).where(Catalog.title == catalog_title))
    else:
        query = await session.execute(select(Catalog).where(Catalog.logo == catalog_logo))

    return query.scalar()


async def get_subcatalog_all(session: AsyncSession, catalog_id: int):
    query = await session.execute(select(Subcatalog).where(Subcatalog.catalog_id == catalog_id))

    return query.scalars().all()


async def get_subcatalog_one(session: AsyncSession, subcatalog_title: str, catalog_id: int):
    query = await session.execute(
        select(Subcatalog).where(Subcatalog.title == subcatalog_title, Subcatalog.catalog_id == catalog_id)
    )

    return query.scalar()


async def get_country_one(session: AsyncSession, country_id=None, country_name=None):
    if country_id:
        query = await session.execute(select(Country).where(Country.id == country_id))
    else:
        query = await session.execute(select(Country).where(Country.name == country_name))

    return query.scalar()


async def get_country_first(session: AsyncSession):
    query = await session.execute(select(Country))

    return query.scalars().first()


async def get_region_all(session: AsyncSession):
    query = await session.execute(select(Region))

    return query.scalars().all()


async def get_region_one(session: AsyncSession, region_id=None, region_name=None):
    if region_id:
        query = await session.execute(select(Region).where(Region.id == region_id))
    else:
        query = await session.execute(select(Region).where(Region.name == region_name))

    return query.scalar()


async def get_city_all(session: AsyncSession, region_id: int):
    query = await session.execute(select(City).where(City.region_id == region_id))

    return query.scalars().all()


async def get_city_one(session: AsyncSession, city_name: str, region_id: int):
    query = await session.execute(select(City).where(City.name == city_name, City.region_id == region_id))

    return query.scalar()


async def get_currency_one(session: AsyncSession, currency_abbreviation: str):
    query = await session.execute(select(Currency).where(Currency.abbreviation == currency_abbreviation))

    return query.scalar()


async def get_currency_first(session: AsyncSession):
    query = await session.execute(select(Currency))

    return query.scalars().first()


async def get_vacancy_all(session: AsyncSession, subcatalog_id: int):
    query = await session.execute(select(Vacancy).where(Vacancy.subcatalog_id == subcatalog_id))

    return query.scalars().all()


async def get_vacancy_all_active(session: AsyncSession, subcatalog_id: int):
    query = await session.execute(select(Vacancy).where(Vacancy.subcatalog_id == subcatalog_id))

    return query.scalars().all()


async def get_vacancy_one(session: AsyncSession, vacancy_id: int):
    query = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))

    return query.scalar()


async def get_vacancy_one_active(session: AsyncSession, vacancy_id: int):
    query = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))

    return query.scalar()


async def get_vacancy_user_active(session: AsyncSession, vacancy_id: int, user_id: int):
    query = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id, Vacancy.user_id == user_id))

    return query.scalar()


async def get_vacancy_user_all(session: AsyncSession, user_id: int):
    query = await session.execute(select(Vacancy).where(Vacancy.user_id == user_id))

    return query.scalars().all()


async def get_user_one(session: AsyncSession, user_id: int):
    query = await session.execute(select(User).where(User.id == user_id))

    return query.scalar()


async def get_favorite_all(session: AsyncSession, user_id: int):
    query = await session.execute(select(Liked).where(Liked.user_id == user_id).options(joinedload(Liked.vacancy)))

    return query.scalars().all()


async def get_favorite_one(session: AsyncSession, user_id: int, vacancy_id: int):
    query = await session.execute(select(Liked).where(Liked.user_id == user_id, Liked.vacancy_id == vacancy_id))

    return query.scalar()


# ########################################   VACANCY   ############################################### #

async def create_vacancy(
        session: AsyncSession,
        name,
        description,
        experience,
        language,
        disability,
        salary,
        subcatalog_id,
        currency_id,
        country_id,
        region_id,
        city_id,
        user_id,
) -> None:
    session.add(Vacancy(
        name=name,
        description=description,
        experience=experience,
        language=language,
        disability=disability,
        salary=salary,
        currency_id=currency_id,
        subcatalog_id=subcatalog_id,
        country_id=country_id,
        region_id=region_id,
        city_id=city_id,
        user_id=user_id,
    ))

    await session.commit()


# ########################################   LIKED   ############################################### #

async def create_liked(
        session: AsyncSession,
        user_id,
        vacancy_id,
) -> None:
    session.add(Liked(
        user_id=user_id,
        vacancy_id=vacancy_id,
    ))

    await session.commit()


async def get_liked_one(session: AsyncSession, user_id: int, vacancy_id: int):
    if user_id and vacancy_id:
        query = await session.execute(select(Liked).where(Liked.user_id == user_id, Liked.vacancy_id == vacancy_id))

        return query.scalar()
    else:
        return None


async def delete_liked_one(session: AsyncSession, user_id: int, vacancy_id: int):
    await session.execute(delete(Liked).where(Liked.user_id == user_id, Liked.vacancy_id == vacancy_id))

    await session.commit()


# ########################################   LIKED   ############################################### #

async def create_complaint(
        session: AsyncSession,
        user_id,
        vacancy_id,
) -> None:
    session.add(Complaint(
        user_id=user_id,
        vacancy_id=vacancy_id,
    ))

    await session.commit()


async def get_complaint_one(session: AsyncSession, user_id: int, vacancy_id: int):
    if user_id and vacancy_id:
        query = await session.execute(select(Complaint).where(Complaint.user_id == user_id, Complaint.vacancy_id == vacancy_id))

        return query.scalar()


async def delete_complaint_one(session: AsyncSession, user_id: int, vacancy_id: int):
    await session.execute(delete(Complaint).where(Complaint.user_id == user_id, Complaint.vacancy_id == vacancy_id))

    await session.commit()
