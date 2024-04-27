from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import City
from core.database.querys import search_user, get_vacancy_one, get_currency_one, get_country_one, get_region_one, \
    get_city_one, get_language_one, get_vacancy_user
from core.utils.connector import connector


async def get_message_vacancy(
        *,
        session: AsyncSession,
        lang: str,
        vacancy_id: int,
        preview: str,
        city: City | None = None
):
    vacancy = await get_vacancy_one(session=session, vacancy_id=vacancy_id)
    user = await search_user(session=session, user_id=vacancy.user_id)
    currency = await get_currency_one(session=session, currency_id=vacancy.currency_id)
    country = await get_country_one(session=session, country_id=vacancy.country_id)
    region = await get_region_one(session=session, region_id=vacancy.region_id)

    if vacancy.city_id:
        city = await get_city_one(session=session, city_id=vacancy.city_id)

    text = f"<b>{vacancy.name}</b>\n\n"

    if preview == 'full':
        text += (f"📝 <b>{connector[lang]['message']['preview']['description']}</b>\n{vacancy.description}\n\n"
                 f"🎯 <b>{connector[lang]['message']['preview']['requirement']}</b>\n{vacancy.requirement}\n\n")

    text += (f"🧩 <b>{connector[lang]['message']['preview']['employment']['caption']}</b>  "
             f"{connector[lang]['message']['preview']['employment']['complete'] if vacancy.employment else connector[lang]['message']['preview']['employment']['incomplete']}\n\n"
             f"💼 <b>{connector[lang]['message']['preview']['experience']['caption']}</b>  "
             f"{connector[lang]['message']['preview']['experience']['yes'] if vacancy.experience else connector[lang]['message']['preview']['experience']['not']}\n\n")

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
        text += (f"☎️ <b>{connector[lang]['message']['preview']['user']['caption']}</b>\n"
                 f"{user.first_name}  /  {'+' + str(user.phone_number) if '+' not in str(user.phone_number) else str(user.phone_number)}\n\n")

    text += f"🗺 <b>{connector[lang]['country'][country.name]['region'][region.name]['name']} {connector[lang]['message']['preview']['location']['region']}</b>"

    if city:
        text += f"<b>  /  {connector[lang]['country'][country.name]['region'][region.name]['city'][city.name]}</b>"

    return text


async def get_message_profile(
        *,
        session: AsyncSession,
        lang: str,
        user_id: int,
):
    user = await search_user(session=session, user_id=user_id)
    country = await get_country_one(session=session, country_id=user.country_id)
    language = await get_language_one(session=session, language_id=user.language_id)
    vacancy = await get_vacancy_user(session=session, user_id=user_id)

    text = f"🧑‍💻 <b>{connector[lang]['message']['profile']['caption']}</b>\n\n<b># {user.username}</b>\n\n"

    if user.first_name:
        text += f"<i>{connector[lang]['message']['profile']['name']}</i>  {user.first_name}\n"

    text += (f"<i>{connector[lang]['message']['profile']['phone']}</i>  +{user.phone_number}\n"
             f"<i>{connector[lang]['message']['profile']['country']}</i>  {country.flag} {connector[lang]['country'][country.name]['name']}\n\n"
             f"<i>{connector[lang]['message']['profile']['language']}</i>  {language.flag} {language.title}\n\n")

    if vacancy:
        activate = 0
        deactivate = 0

        for check in vacancy:
            if check.active:
                activate += 1
            else:
                deactivate += 1

        text += (f"<i>{connector[lang]['message']['profile']['vacancy']['has']['activate']}</i>  <b>{activate}</b>\n"
                 f"<i>{connector[lang]['message']['profile']['vacancy']['has']['deactivate']}</i>  <b>{deactivate}</b>\n\n")
    else:
        text += f"❎ <b>{connector[lang]['message']['profile']['vacancy']['not']}</b>\n\n"

    text += (f"<i>{connector[lang]['message']['profile']['create']}</i>  "
             f"{'0' + str(user.created.day) if len(str(user.created.day)) == 1 else user.created.day}."
             f"{'0' + str(user.created.month) if len(str(user.created.month)) == 1 else user.created.month}."
             f"{user.created.year}")

    return text
