from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Base, Language, Currency, Country, Region, City, Catalog, Subcatalog
from core.database.querys import get_language_one, get_currency_one, get_catalog_one, get_subcatalog_one, \
    get_country_one, get_region_one, get_city_one, search_user, create_user
from core.utils.settings import async_engine, async_session_maker, admin
from core.utils.username import create_username


creator = {
    'language': {
        'uk': {
            'title': 'Українська',
            'flag': '🇺🇦',
        },
    },

    'currency': ['UAH'],

    'catalog': {
        'construction': {
            'logo': '🧱',
            'sub': ['cranes_man', 'tiler', 'fitter', 'welder', 'painter',
                    'plumber', 'facade_man', 'plasterer', 'electrician', 'other'],
        },
        'medical': {
            'logo': '💊',
            'sub':  ['nurse', 'dentist', 'pharmacist', 'veterinarian', 'other'],
        },
        'it': {
            'logo': '🖥',
            'sub':  ['sysadmin', 'operator', 'developer', 'gamedev', 'repairman', 'other'],
        },
        'finances': {
            'logo': '💰',
            'sub':  ['lawyer', 'other'],
        },
        'realestate': {
            'logo': '🏠',
            'sub':  ['realtor', 'broker', 'other'],
        },
    },

    'country': {
        'uk': {
            'flag': '🇺🇦',
            'region': {
                'vinnytsia': [
                    'vinnytsia', 'zhmerynka', 'mogilev', 'khmelnyk',
                ],
                'volyn': [
                    'vladimir', 'kovel', 'lutsk', 'novovolynsk',
                ],
                'dnipropetrovsk': [
                    'dnieper', 'zhovti', 'kamenskoye', 'krivoy', 'manganets', 'nikopol', 'novomoskovsk',
                    'pokrov', 'pavlograd', 'sinelnikovo',
                ],
                'donetsk': [
                    'avdeevka', 'bakhmut', 'gorlovka', 'donetsk', 'druzhkovka', 'yenakievo', 'konstantinovka',
                    'kramatorsk', 'makeevka', 'mariupol', 'slavyansk', 'snezhnoye', 'chistyakovo', 'toretsk',
                    'khartsyzk', 'shakhtersk', 'yasinovataya',
                ],
                'zakarpattia': [
                    'beregovo', 'vinogradov', 'irshava', 'mukachevo', 'uzhgorod', 'khust',
                ],
                'zaporizhia': [
                    'berdyansk', 'zaporozhye', 'melitopol', 'tokmak', 'energodar',
                ],
                'zhytomyr': [
                    'berdichev', 'zhytomyr', 'korosten', 'novograd',
                ],
                'frankivsk': [
                    'frankivsk', 'kalush', 'kolomyia',
                ],
                'kiev': [
                    'church', 'boryspil', 'boyarka', 'brovary', 'bucha', 'vasilkov', 'vishnevoye', 'vyshgorod',
                    'irpen', 'kiev', 'obukhov', 'slavutich', 'fastov',
                ],
                'kirovohrad': [
                    'alexandria', 'kropivnitsky', 'svetlovodsk',
                ],
                'lviv': [
                    'boryslav', 'drohobych', 'lviv', 'novoyavorovsk', 'sambor', 'stryj', 'chervonograd',
                ],
                'luhansk': [
                    'alchevsk', 'anthracite', 'bryanka', 'sorokino', 'khrustalny', 'lisichansk', 'lugansk', 'pervomaysk',
                    'rovenky', 'rubizhne', 'sverdlovsk', 'severodonetsk', 'stakhanov',
                ],
                'mykolaiv': [
                    'voznesensk', 'mykolaiv', 'pervomaysk', 'yuzhnoukrainsk',
                ],
                'odessa': [
                    'belgorod', 'izmail', 'odessa', 'podolsk', 'chernomorsk', 'yuzhnoye',
                ],
                'poltava': [
                    'plavni', 'kremenchug', 'lubny', 'mirgorod', 'poltava',
                ],
                'rivne': [
                    'dubno', 'kostopol', 'varasch', 'rivne',
                ],
                'sumy': [
                    'ochtirka', 'glukhov', 'konotop', 'romney', 'sumy', 'shostka',
                ],
                'ternopil': [
                    'kremenets', 'ternopil', 'chortkiv',
                ],
                'kharkiv': [
                    'izyum', 'lozovaya', 'pervomayskiy', 'kharkiv', 'chuguev',
                ],
                'kherson': [
                    'alyoshki', 'kakhovka', 'novaya', 'kherson',
                ],
                'khmelnytskyi': [
                    'podilskyi', 'neteszyn', 'slavuta', 'starokonstantinov', 'kmelnytskyi', 'shepetivka',
                ],
                'cherkasy': [
                    'zolotonosha', 'smela', 'uman', 'cherkasy',
                ],
                'chernivtsi': [
                    'novodnestrovsk', 'storozyniec', 'chernivtsi',
                ],
                'chernihiv': [
                    'nizhyn', 'priluki', 'chernigov',
                ],
            },
        },
    },
}


async def create_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
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
        lang = await get_language_one(session=session, language_abbreviation=key)
        if not lang:
            session.add(Language(abbreviation=key, title=info['title'], flag=info['flag']))

    await session.commit()


async def create_currency(session: AsyncSession, data: list) -> None:
    for currency_abbreviation in data:
        currency = await get_currency_one(session=session, currency_abbreviation=currency_abbreviation)
        if not currency:
            session.add(Currency(abbreviation=currency_abbreviation))

    await session.commit()


async def create_catalog(session: AsyncSession, data: dict) -> None:
    for title, info in data.items():
        catalog = await get_catalog_one(session=session, catalog_title=title)
        if not catalog:
            session.add(Catalog(title=title, logo=info['logo']))

    await session.commit()


async def create_subcatalog(session: AsyncSession, data: dict) -> None:
    for title, info in data.items():
        catalog = await get_catalog_one(session=session, catalog_title=title)
        for subcatalog_title in info['sub']:
            subcatalog = await get_subcatalog_one(session=session, catalog_id=catalog.id, subcatalog_title=subcatalog_title)
            if not subcatalog:
                session.add(Subcatalog(title=subcatalog_title, catalog_id=catalog.id))

    await session.commit()


async def create_country(session: AsyncSession, data: dict) -> None:
    for name, info in data.items():
        country = await get_country_one(session=session, country_name=name)
        if not country:
            session.add(Country(name=name, flag=info['flag']))

    await session.commit()


async def create_region(session: AsyncSession, data: dict) -> None:
    for country_name, info in data.items():
        country = await get_country_one(session=session, country_name=country_name)
        for region_name, _ in info['region'].items():
            region = await get_region_one(session=session, region_name=region_name)
            if not region:
                session.add(Region(name=region_name, country_id=country.id))

    await session.commit()


async def create_city(session: AsyncSession, data: dict) -> None:
    for country_name, info in data.items():
        for region_name, city_name in info['region'].items():
            region = await get_region_one(session=session, region_name=region_name)
            for name in city_name:
                city = await get_city_one(session=session, city_name=name)
                if not city:
                    session.add(City(name=name, region_id=region.id))

    await session.commit()


async def create_admin(session: AsyncSession) -> None:
    user_exist = await search_user(
        session=session,
        user_id=admin['id'],
    )

    if not user_exist:
        lang = await get_language_one(
            session=session,
            language_abbreviation='uk',
        )
        country = await get_country_one(
            session=session,
            country_name='uk',
        )
        currency = await get_currency_one(
            session=session,
            currency_abbreviation='UAH',
        )

        await create_user(
            session=session,
            user_id=admin['id'],
            username=await create_username(session=session),
            first_name=admin['name'],
            phone_number=admin['phone'],
            language_id=lang.id,
            currency_id=currency.id,
            country_id=country.id,
            is_admin=True,
        )
