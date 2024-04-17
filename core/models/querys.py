from sqlalchemy import select, update, delete, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.models import Language, User, Separator, Currency, Catalog, Subcatalog, Country, Region, City, Vacancy, Liked, Complaint, Transaction  # noqa


# ########################################   USER   ############################################### #

async def create_user(*, session: AsyncSession, user_id, username, first_name, phone_number, language_id, is_admin=False) -> None:
    session.add(User(
        id=user_id,
        username=username,
        first_name=first_name,
        phone_number=phone_number,
        is_admin=is_admin,
        language_id=language_id,
    ))

    await session.commit()


async def search_user(*, session: AsyncSession, user_id: int | None = None, username: str | None = None):
    query = await session.execute(select(User).where(
        or_(user_id is None, User.id == user_id),
        or_(username is None, User.username == username),
    ))

    return query.scalar()


# ########################################   FILTER   ############################################### #

async def create_separator(*, session: AsyncSession, user_id, currency_id, country_id) -> None:
    session.add(Separator(
        id=user_id,
        currency_id=currency_id,
        country_id=country_id,
    ))

    await session.commit()


# ########################################   VACANCY   ############################################### #

async def create_vacancy(*, session: AsyncSession, data: dict, user_id: int) -> None:
    session.add(Vacancy(
        name=data['name'],
        description=data['description'],
        experience=data['experience'],
        language=data['language'],
        disability=data['disability'],
        salary=data['salary'],
        catalog_id=data['catalog_id'],
        subcatalog_id=data['subcatalog_id'],
        currency_id=data['currency_id'],
        country_id=data['country_id'],
        region_id=data['region_id'],
        city_id=data['city_id'],
        user_id=user_id,
    ))

    await session.commit()


async def update_vacancy(*, session: AsyncSession, data: dict, vacancy_id: int) -> None:
    await session.execute(
        update(Vacancy).where(Vacancy.id == vacancy_id).values(
            name=data['name'],
            description=data['description'],
            experience=data['experience'],
            language=data['language'],
            disability=data['disability'],
            salary=data['salary'],
            catalog_id=data['catalog_id'],
            subcatalog_id=data['subcatalog_id'],
            currency_id=data['currency_id'],
            country_id=data['country_id'],
            region_id=data['region_id'],
            city_id=data['city_id'],
        )
    )

    await session.commit()


async def get_vacancy_complaint(*, session: AsyncSession, vacancy_id: int, operation: str) -> None:
    await session.execute(
        update(Vacancy).where(Vacancy.id == vacancy_id).values(
            complaint=Vacancy.count_complaint + 1 if operation == 'plus' else Vacancy.count_complaint - 1,
        )
    )

    await session.commit()


async def deactivate_vacancy(*, session: AsyncSession, vacancy_id: int) -> None:
    await session.execute(
        update(Vacancy).where(Vacancy.id == vacancy_id).values(
            active=False,
        )
    )

    await session.commit()


# ########################################   LIKED   ############################################### #

async def create_liked(*, session: AsyncSession, user_id: int, vacancy_id: int) -> None:
    session.add(Liked(
        user_id=user_id,
        vacancy_id=vacancy_id,
    ))

    await session.commit()


async def delete_liked(*, session: AsyncSession, user_id: int, vacancy_id: int) -> None:
    await session.execute(delete(Liked).where(Liked.user_id == user_id, Liked.vacancy_id == vacancy_id))

    await session.commit()


# ########################################   LIKED   ############################################### #

async def create_complaint(*, session: AsyncSession, user_id: int, vacancy_id: int) -> None:
    session.add(Complaint(
        user_id=user_id,
        vacancy_id=vacancy_id,
    ))

    await session.commit()


async def delete_complaint(*, session: AsyncSession, user_id: int, vacancy_id: int) -> None:
    await session.execute(delete(Complaint).where(Complaint.user_id == user_id, Complaint.vacancy_id == vacancy_id))

    await session.commit()


# ########################################   GET DATA   ############################################### #

async def get_language_one(*, session: AsyncSession, language_id: int | None = None, language_abbreviation: str | None = None):
    query = await session.execute(select(Language).where(
        or_(language_id is None, Language.id == language_id),
        or_(language_abbreviation is None, Language.abbreviation == language_abbreviation),
    ))

    return query.scalar()


async def get_catalog_all(*, session: AsyncSession):
    query = await session.execute(select(Catalog))

    return query.scalars().all()


async def get_catalog_one(*, session: AsyncSession, catalog_id: str | None = None, catalog_title: str | None = None, catalog_logo: str | None = None):
    query = await session.execute(select(Catalog).where(
        or_(catalog_id is None, Catalog.id == catalog_id),
        or_(catalog_title is None, Catalog.title == catalog_title),
        or_(catalog_logo is None, Catalog.logo == catalog_logo),
    ))

    return query.scalar()


async def get_subcatalog_all(*, session: AsyncSession, catalog_id: int):
    query = await session.execute(select(Subcatalog).where(Subcatalog.catalog_id == catalog_id))

    return query.scalars().all()


async def get_subcatalog_one(*, session: AsyncSession, catalog_id, subcatalog_id: int | None = None, subcatalog_title: str | None = None):
    query = await session.execute(select(Subcatalog).where(
        or_(subcatalog_id is None, Subcatalog.id == subcatalog_id),
        or_(subcatalog_title is None, Subcatalog.title == subcatalog_title),
        Subcatalog.catalog_id == catalog_id
    ))

    return query.scalar()


async def get_country_one(*, session: AsyncSession, country_id: int | None = None, country_name: str | None = None):
    query = await session.execute(select(Country).where(
        or_(country_id is None, Country.id == country_id),
        or_(country_name is None, Country.name == country_name),
    ))

    return query.scalar()


async def get_country_first(*, session: AsyncSession):
    query = await session.execute(select(Country))

    return query.scalars().first()


async def get_region_all(*, session: AsyncSession):
    query = await session.execute(select(Region))

    return query.scalars().all()


async def get_region_one(*, session: AsyncSession, region_id: int | None = None, region_name: str | None = None):
    query = await session.execute(select(Region).where(
        or_(region_id is None, Region.id == region_id),
        or_(region_name is None, Region.name == region_name),
    ))

    return query.scalar()


async def get_city_all(*, session: AsyncSession, region_id: int):
    query = await session.execute(select(City).where(City.region_id == region_id))

    return query.scalars().all()


async def get_city_one(*, session: AsyncSession, city_id: int | None = None, city_name: str | None = None):
    query = await session.execute(select(City).where(
        or_(city_id is None, City.id == city_id),
        or_(city_name is None, City.name == city_name),
    ))

    return query.scalar()


async def get_currency_one(*, session: AsyncSession, currency_abbreviation: str):
    query = await session.execute(select(Currency).where(Currency.abbreviation == currency_abbreviation))

    return query.scalar()


async def get_currency_first(*, session: AsyncSession):
    query = await session.execute(select(Currency))

    return query.scalars().first()


async def get_vacancy_all_active(*, session: AsyncSession, subcatalog_id: int):
    query = await session.execute(select(Vacancy).where(
        Vacancy.subcatalog_id == subcatalog_id,
        Vacancy.active,
        or_(Vacancy.count_complaint < 5, Vacancy.count_complaint > 5),
    ))

    return query.scalars().all()


async def get_vacancy_one(*, session: AsyncSession, vacancy_id: int, user_id: int | None = None):
    query = await session.execute(select(Vacancy).where(
        Vacancy.id == vacancy_id,
        Vacancy.active,
        or_(user_id is None, Vacancy.user_id == user_id),
    ))

    return query.scalar()


async def get_vacancy_user(*, session: AsyncSession, user_id: int):
    query = await session.execute(select(Vacancy).where(
        Vacancy.user_id == user_id,
        Vacancy.active,
    ))

    return query.scalars().all()


async def get_favorite_vacancy(*, session: AsyncSession, user_id: int):
    query = await session.execute(select(Liked).where(Liked.user_id == user_id).options(joinedload(Liked.vacancy)))

    return query.scalars().all()


async def get_complaint_one(*, session: AsyncSession, user_id: int, vacancy_id: int):
    query = await session.execute(select(Complaint).where(Complaint.user_id == user_id, Complaint.vacancy_id == vacancy_id))

    return query.scalar()


async def get_liked_one(*, session: AsyncSession, user_id: int, vacancy_id: int):
    query = await session.execute(select(Liked).where(Liked.user_id == user_id, Liked.vacancy_id == vacancy_id))

    return query.scalar()
