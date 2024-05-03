from sqlalchemy import select, update, delete, or_
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Language, Currency, Catalog, Subcatalog, Country, Region, City, User, Vacancy, \
    Preview, Liked, Complaint
from core.utils.settings import admin


# ########################################   USER   ############################################### #

async def create_user(
        *,
        session: AsyncSession,
        user_id,
        username,
        first_name,
        phone_number,
        language_id,
        currency_id,
        country_id,
        is_admin=False,
) -> None:
    session.add(
        User(
            id=user_id,
            username=username,
            first_name=first_name,
            phone_number=phone_number,
            language_id=language_id,
            currency_id=currency_id,
            country_id=country_id,
            is_admin=is_admin,
        )
    )

    await session.commit()


async def update_name_user(
        *,
        session: AsyncSession,
        user_id: int,
        first_name: str,
) -> None:
    await session.execute(
        update(
            User,
        ).where(
            User.id == user_id,
        ).values(
            first_name=first_name,
        )
    )

    await session.commit()


async def blocked_user(
        *,
        session: AsyncSession,
        user_id: int,
) -> None:
    await session.execute(
        update(
            User,
        ).where(
            User.id == user_id,
        ).values(
            blocked=True,
        )
    )

    await session.commit()


# ########################################   VACANCY   ############################################### #

async def create_vacancy(
        *,
        session: AsyncSession,
        data: dict,
        user_id: int,
):
    vacancy = Vacancy(
        name=data['name'],
        description=data['description'],
        requirement=data['requirement'],
        employment=data['employment'],
        experience=data['experience'],
        schedule=data['schedule'],
        remote=data['remote'],
        language=data['language'],
        foreigner=data['foreigner'],
        disability=data['disability'],
        salary=data['salary'],
        catalog_id=data['catalog_id'],
        subcatalog_id=data['subcatalog_id'],
        currency_id=data['currency_id'],
        country_id=data['country_id'],
        region_id=data['region_id'],
        city_id=data['city_id'],
        user_id=user_id,
    )
    session.add(vacancy)

    await session.commit()

    return vacancy


async def update_vacancy(
        *,
        session: AsyncSession,
        data: dict,
        vacancy_id: int,
) -> None:
    await session.execute(
        update(
            Vacancy,
        ).where(
            Vacancy.id == vacancy_id,
        ).values(
            name=data['name'],
            description=data['description'],
            requirement=data['requirement'],
            employment=data['employment'],
            experience=data['experience'],
            schedule=data['schedule'],
            remote=data['remote'],
            language=data['language'],
            foreigner=data['foreigner'],
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


async def update_channel(
        *,
        session: AsyncSession,
        vacancy_id: int,
        channel_id: int,
) -> None:
    await session.execute(
        update(
            Vacancy,
        ).where(
            Vacancy.id == vacancy_id,
        ).values(
            channel_id=channel_id,
        )
    )

    await session.commit()


async def deactivate_vacancy(
        *,
        session: AsyncSession,
        vacancy_id: int,
        method: str,
) -> None:
    await session.execute(
        update(
            Vacancy,
        ).where(
            Vacancy.id == vacancy_id,
        ).values(
            active=True if method == 'activate' else False,
        )
    )

    await session.commit()


async def delete_vacancy(
        *,
        session: AsyncSession,
        vacancy_id: int,
) -> None:
    await session.execute(
        delete(
            Vacancy,
        ).where(
            Vacancy.id == vacancy_id,
        )
    )

    await session.commit()


async def delete_vacancy_user(
        *,
        session: AsyncSession,
        user_id: int,
) -> None:
    await session.execute(
        delete(
            Vacancy,
        ).where(
            Vacancy.user_id == user_id,
        )
    )

    await session.commit()


# ########################################   PREVIEW   ############################################### #

async def create_preview(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
) -> None:
    session.add(
        Preview(
            user_id=user_id,
            vacancy_id=vacancy_id,
        )
    )

    await session.commit()


# ########################################   LIKED   ############################################### #

async def create_liked(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
) -> None:
    session.add(
        Liked(
            user_id=user_id,
            vacancy_id=vacancy_id,
        )
    )

    await session.commit()


async def delete_liked(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
) -> None:
    await session.execute(
        delete(
            Liked,
        ).where(
            Liked.user_id == user_id,
            Liked.vacancy_id == vacancy_id,
        )
    )

    await session.commit()


# ########################################   LIKED   ############################################### #

async def create_complaint(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
) -> None:
    session.add(
        Complaint(
            user_id=user_id,
            vacancy_id=vacancy_id,
        )
    )

    await session.commit()


async def delete_complaint(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
) -> None:
    await session.execute(
        delete(
            Complaint,
        ).where(
            Complaint.user_id == user_id,
            Complaint.vacancy_id == vacancy_id,
        )
    )

    await session.commit()


# ########################################   GET DATA   ############################################### #

async def search_user(
        *,
        session: AsyncSession,
        user_id: int | None = None,
        username: str | None = None,
):
    query = await session.execute(
        select(
            User,
        ).where(
            or_(user_id is None, User.id == user_id),
            or_(username is None, User.username == username),
        )
    )

    return query.scalar()


async def user_profile(
        *,
        session: AsyncSession,
        user_id: int,
):
    query = await session.execute(
        select(
            User,
        ).where(
            User.id == user_id,
        ).filter(
            User.language_id == Language.id,
        ).options(
            selectinload(
                User.language,
            )
        ).filter(
            User.currency_id == Currency.id,
        ).options(
            selectinload(
                User.currency,
            )
        ).filter(
            User.country_id == Country.id,
        ).options(
            selectinload(
                User.country,
            )
        )
    )

    return query.scalar()


async def get_language_one(
        *,
        session: AsyncSession,
        language_id: int | None = None,
        language_abbreviation: str | None = None,
):
    query = await session.execute(
        select(
            Language,
        ).where(
            or_(language_id is None, Language.id == language_id),
            or_(language_abbreviation is None, Language.abbreviation == language_abbreviation),
        )
    )

    return query.scalar()


async def get_language_user(
        *,
        session: AsyncSession,
        user_id: int,
):
    query = await session.execute(
        select(
            User,
        ).where(
            User.id == user_id,
        ).join(
            User.language
        ).options(
            joinedload(
                User.language,
            )
        )
    )

    return query.scalar()


async def get_catalog_all(
        *,
        session: AsyncSession,
):
    query = await session.execute(
        select(
            Catalog,
        )
    )

    return query.scalars().all()


async def get_catalog_one(
        *,
        session: AsyncSession,
        catalog_id: int | None = None,
        catalog_title: str | None = None,
        catalog_logo: str | None = None,
):
    query = await session.execute(
        select(
            Catalog,
        ).where(
            or_(catalog_id is None, Catalog.id == catalog_id),
            or_(catalog_title is None, Catalog.title == catalog_title),
            or_(catalog_logo is None, Catalog.logo == catalog_logo),
        )
    )

    return query.scalar()


async def get_subcatalog_all(
        *,
        session: AsyncSession,
        catalog_id: int,
):
    query = await session.execute(
        select(
            Subcatalog,
        ).where(
            Subcatalog.catalog_id == catalog_id,
        )
    )

    return query.scalars().all()


async def get_subcatalog_one(
        *,
        session: AsyncSession,
        catalog_id,
        subcatalog_id: int | None = None,
        subcatalog_title: str | None = None,
):
    query = await session.execute(
        select(
            Subcatalog,
        ).where(
            or_(subcatalog_id is None, Subcatalog.id == subcatalog_id),
            or_(subcatalog_title is None, Subcatalog.title == subcatalog_title),
            Subcatalog.catalog_id == catalog_id,
        )
    )

    return query.scalar()


async def get_country_one(
        *,
        session: AsyncSession,
        country_id: int | None = None,
        country_name: str | None = None,
):
    query = await session.execute(
        select(
            Country,
        ).where(
            or_(country_id is None, Country.id == country_id),
            or_(country_name is None, Country.name == country_name),
        )
    )

    return query.scalar()


async def get_country_first(*, session: AsyncSession):
    query = await session.execute(
        select(
            Country,
        )
    )

    return query.scalars().first()


async def get_region_all(
        *,
        session: AsyncSession,
        country_id: int,
):
    query = await session.execute(
        select(
            Region,
        ).where(
            Region.country_id == country_id,
        )
    )

    return query.scalars().all()


async def get_region_one(
        *,
        session: AsyncSession,
        region_id: int | None = None,
        region_name: str | None = None,
):
    query = await session.execute(
        select(
            Region,
        ).where(
            or_(region_id is None, Region.id == region_id),
            or_(region_name is None, Region.name == region_name),
        )
    )

    return query.scalar()


async def get_city_all(
        *,
        session: AsyncSession,
        region_id: int,
):
    query = await session.execute(
        select(
            City,
        ).where(
            City.region_id == region_id,
        )
    )

    return query.scalars().all()


async def get_city_one(
        *,
        session: AsyncSession,
        city_id: int | None = None,
        city_name: str | None = None,
):
    query = await session.execute(
        select(
            City
        ).where(
            or_(city_id is None, City.id == city_id),
            or_(city_name is None, City.name == city_name),
        )
    )

    return query.scalar()


async def get_currency_one(
        *,
        session: AsyncSession,
        currency_id: int | None = None,
        currency_abbreviation: str | None = None,
):
    query = await session.execute(
        select(
            Currency,
        ).where(
            or_(currency_id is None, Currency.id == currency_id),
            or_(currency_abbreviation is None, Currency.abbreviation == currency_abbreviation),
        )
    )

    return query.scalar()


async def get_currency_first(
        *,
        session: AsyncSession,
):
    query = await session.execute(
        select(
            Currency,
        )
    )

    return query.scalars().first()


async def get_vacancy_all_active(
        *,
        session: AsyncSession,
        subcatalog_id: int,
):
    query = await session.execute(
        select(
            Vacancy,
        ).where(
            Vacancy.active,
            Vacancy.subcatalog_id == subcatalog_id,
        ).select_from(
            Vacancy
        ).join(
            Complaint,
            Vacancy.id == Complaint.vacancy_id,
            full=True,
        ).group_by(
            Vacancy.id,
        ).having(
            func.count(Complaint.vacancy_id) != 10,
        ))

    return query.scalars().all()


async def get_vacancy_one(
        *,
        session: AsyncSession,
        vacancy_id: int,
        user_id: int | None = None,
):
    query = await session.execute(
        select(
            Vacancy,
        ).where(
            Vacancy.id == vacancy_id,
            or_(user_id is None, Vacancy.user_id == user_id),
        )
    )

    return query.scalar()


async def get_vacancy_user(
        *,
        session: AsyncSession,
        user_id: int,
):
    query = await session.execute(
        select(
            Vacancy,
        ).where(
            Vacancy.user_id == user_id,
        )
    )

    return query.scalars().all()


async def get_vacancy_favorite(
        *,
        session: AsyncSession,
        user_id: int,
):
    query = await session.execute(
        select(
            Vacancy,
        ).where(
            Vacancy.active,
            Liked.user_id == user_id,
        ).select_from(
            Vacancy,
        ).join(
            Liked,
            Vacancy.id == Liked.vacancy_id,
            full=True,
        ).select_from(
            Vacancy,
        ).join(
            Complaint,
            Vacancy.id == Complaint.vacancy_id,
            full=True,
        ).group_by(
            Vacancy.id
        ).having(
            func.count(Complaint.vacancy_id) != 10,
        )
    )

    return query.scalars().all()


async def get_vacancy_preview(
        *,
        session: AsyncSession,
        vacancy_id: int,
):
    query = await session.execute(
        select(
            Vacancy,
        ).where(
            Vacancy.id == vacancy_id,
        ).filter(
            Vacancy.user_id == User.id,
        ).options(
            selectinload(
                Vacancy.user,
            )
        ).filter(
            Vacancy.currency_id == Currency.id,
        ).options(
            selectinload(
                Vacancy.currency,
            )
        ).filter(
            Vacancy.catalog_id == Catalog.id,
        ).options(
            selectinload(
                Vacancy.catalog,
            )
        ).filter(
            Vacancy.country_id == Country.id,
        ).options(
            selectinload(
                Vacancy.country,
            )
        ).filter(
            Vacancy.region_id == Region.id,
        ).options(
            selectinload(
                Vacancy.region,
            )
        )
    )

    return query.scalar()


async def get_vacancy_admin(
        *,
        session: AsyncSession,
):
    query = await session.execute(
        select(
            Vacancy,
        ).where(
            Vacancy.user_id != admin['id'],
            Vacancy.active,
        ).select_from(
            Vacancy
        ).join(
            Complaint,
            Vacancy.id == Complaint.vacancy_id,
            full=True,
        ).group_by(
            Vacancy.id,
        ).having(
            func.count(Complaint.vacancy_id) == 10,
        )
    )

    return query.scalars().all()


async def get_preview_one(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
):
    query = await session.execute(
        select(
            Preview,
        ).where(
            Preview.user_id == user_id,
            Preview.vacancy_id == vacancy_id,
        )
    )

    return query.scalar()


async def get_complaint_one(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
):
    query = await session.execute(
        select(
            Complaint,
        ).where(
            Complaint.user_id == user_id,
            Complaint.vacancy_id == vacancy_id,
        )
    )

    return query.scalar()


async def get_complaint_count(
        *,
        session: AsyncSession,
        vacancy_id: int,
):
    query = await session.execute(
        select(
            func.count(Complaint.vacancy_id).label("complaint_count"),
        ).where(
            Complaint.vacancy_id == vacancy_id,
        )
    )

    return query.one()


async def get_liked_one(
        *,
        session: AsyncSession,
        user_id: int,
        vacancy_id: int,
):
    query = await session.execute(
        select(
            Liked,
        ).where(
            Liked.user_id == user_id,
            Liked.vacancy_id == vacancy_id,
        )
    )

    return query.scalar()
