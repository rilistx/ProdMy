from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import City
from core.database.querys import search_user, get_vacancy_one, get_currency_one, get_country_one, get_region_one, \
    get_city_one, get_language_one, get_vacancy_user
from core.utils.connector import connector


async def get_message_registration_start(
        *,
        lang: str,
) -> str:
    text = (
        f"<b>{connector[lang]['start_message']['hello']}</b> 👋🏻\n\n"
        f"🤖 <b>{connector[lang]['start_message']['caption']}</b>\n"
        f"{connector[lang]['start_message']['about']}\n\n"
        f"🚀 <i>{connector[lang]['start_message']['expression']}</i>\n\n"
        f"💡 {connector[lang]['start_message']['stipulation']} "
        f"\"<b>{connector[lang]['button']['registration']['contact']}</b>\""
    )

    return text


async def get_text_registration_contact(
        *,
        lang: str,
) -> str:
    text = (
        f"<b>{connector[lang]['message']['registration']['contact']['greeting']}</b> 🎉\n\n"
        f"<i>{connector[lang]['message']['registration']['contact']['success']}</i>\n\n"
        f"<blockquote>⚙️ {connector[lang]['message']['registration']['contact']['support']}</blockquote>"
    )

    return text


def get_text_vacancy_create(
        *,
        lang: str,
        func_name: str,
        change: bool | None = None,
        text: str | None = None,
) -> str:
    if func_name == 'exit':
        if change:
            text = connector[lang]['message']['vacancy']['exit']['change']
        else:
            text = connector[lang]['message']['vacancy']['exit']['create']
    elif func_name == 'change':
        if change:
            text = connector[lang]['message']['vacancy']['finish']['change']
        else:
            text = connector[lang]['message']['vacancy']['finish']['nochange']
    elif func_name == 'create':
        text = connector[lang]['message']['vacancy']['finish']['create']
    else:
        func_list = [
            'catalog', 'subcatalog', 'name', 'description', 'requirement', 'employment', 'experience',
            'remote', 'language', 'foreigner', 'disability', 'salary', 'region', 'city',
        ]

        for key in func_list:
            if key == func_name:
                text = connector[lang]['message']['vacancy'][func_name]

        if change:
            text += connector[lang]['message']['vacancy']['add']

    return text


async def get_message_vacancy_preview(
        *,
        session: AsyncSession,
        lang: str,
        vacancy_id: int,
        preview: str,
        city: City | None = None
) -> str:
    vacancy = await get_vacancy_one(session=session, vacancy_id=vacancy_id)
    user = await search_user(session=session, user_id=vacancy.user_id)
    currency = await get_currency_one(session=session, currency_id=vacancy.currency_id)
    country = await get_country_one(session=session, country_id=vacancy.country_id)
    region = await get_region_one(session=session, region_id=vacancy.region_id)

    if vacancy.city_id:
        city = await get_city_one(session=session, city_id=vacancy.city_id)

    text = f"<b>{vacancy.name}</b>\n\n"

    if preview == 'full':
        text += (
            f"📝 <b>{connector[lang]['message']['preview']['description']}</b>\n{vacancy.description}\n\n"
            f"🎯 <b>{connector[lang]['message']['preview']['requirement']}</b>\n{vacancy.requirement}\n\n"
        )

    if vacancy.employment:
        employment = connector[lang]['message']['preview']['employment']['complete']
    else:
        employment = connector[lang]['message']['preview']['employment']['incomplete']

    if vacancy.experience:
        experience = connector[lang]['message']['preview']['experience']['yes']
    else:
        experience = connector[lang]['message']['preview']['experience']['not']

    text += (
        f"🧩 <b>{connector[lang]['message']['preview']['employment']['caption']}</b>  {employment}\n\n"
        f"💼 <b>{connector[lang]['message']['preview']['experience']['caption']}</b>  {experience}\n"
    )

    if vacancy.remote or vacancy.language or vacancy.foreigner or vacancy.disability:
        text += "\n"
        if vacancy.remote:
            text += f"✅ {connector[lang]['message']['preview']['remote']}\n"

        if vacancy.language:
            text += f"✅ {connector[lang]['message']['preview']['language']}\n"

        if vacancy.foreigner:
            text += f"✅ {connector[lang]['message']['preview']['foreigner']}\n"

        if vacancy.disability:
            text += f"✅ {connector[lang]['message']['preview']['disability']}\n"

    text += f"\n<b>💰 {connector[lang]['message']['preview']['salary']}  {vacancy.salary} {currency.abbreviation}</b>\n\n"

    if preview == 'full':
        if '+' not in str(user.phone_number):
            phone_number = '+' + str(user.phone_number)
        else:
            phone_number = str(user.phone_number)

        text += (
            f"☎️ <b>{connector[lang]['message']['preview']['user']['caption']}</b>\n"
            f"{user.first_name}  /  {phone_number}\n\n"
        )

    text += (
        f"🗺 <b>{connector[lang]['country'][country.name]['region'][region.name]['name']} "
        f"{connector[lang]['message']['preview']['location']['region']}</b>"
    )

    if city:
        text += f"<b>  /  {connector[lang]['country'][country.name]['region'][region.name]['city'][city.name]}</b>"

    return text


async def get_message_profile(
        *,
        session: AsyncSession,
        lang: str,
        user_id: int,
) -> str:
    user = await search_user(session=session, user_id=user_id)
    country = await get_country_one(session=session, country_id=user.country_id)
    language = await get_language_one(session=session, language_id=user.language_id)
    vacancy = await get_vacancy_user(session=session, user_id=user_id)

    text = f"🧑‍💻 <b>{connector[lang]['message']['profile']['caption']}</b>\n\n<b># {user.username}</b>\n\n"

    if user.first_name:
        text += f"<i>{connector[lang]['message']['profile']['name']}</i>  {user.first_name}\n"

    if '+' not in str(user.phone_number):
        phone_number = '+' + str(user.phone_number)
    else:
        phone_number = str(user.phone_number)

    text += (
        f"<i>{connector[lang]['message']['profile']['phone']}</i>  {phone_number}\n"
        f"<i>{connector[lang]['message']['profile']['country']}</i>  {country.flag} {connector[lang]['country'][country.name]['name']}\n\n"
        f"<i>{connector[lang]['message']['profile']['language']}</i>  {language.flag} {language.title}\n\n"
    )

    if vacancy:
        activate = 0
        deactivate = 0

        for check in vacancy:
            if check.active:
                activate += 1
            else:
                deactivate += 1

        text += (
            f"<i>{connector[lang]['message']['profile']['vacancy']['has']['activate']}</i>  <b>{activate}</b>\n"
            f"<i>{connector[lang]['message']['profile']['vacancy']['has']['deactivate']}</i>  <b>{deactivate}</b>\n\n"
        )
    else:
        text += f"❎ <b>{connector[lang]['message']['profile']['vacancy']['not']}</b>\n\n"

    text += (
        f"<i>{connector[lang]['message']['profile']['create']}</i>  "
        f"{'0' + str(user.created.day) if len(str(user.created.day)) == 1 else user.created.day}."
        f"{'0' + str(user.created.month) if len(str(user.created.month)) == 1 else user.created.month}."
        f"{user.created.year}"
    )

    return text
