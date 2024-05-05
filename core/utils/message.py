from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import City
from core.database.querys import user_profile, get_city_one, get_vacancy_user, get_vacancy_preview
from core.utils.connector import connector
from core.utils.settings import credit_cart


async def get_text_registration_start(
        *,
        lang: str,
) -> str:
    text = (
        f"<b>{connector[lang]['start_message']['hello']}</b> 👋🏻\n\n"
        f"🤖 <b>{connector[lang]['start_message']['caption']}?</b>\n"
        f"{connector[lang]['start_message']['about']}\n\n"
        f"🚀 <i>{connector[lang]['start_message']['expression']}</i>\n\n"
        f"💡 {connector[lang]['start_message']['stipulation']} "
        f"\"<b>{connector[lang]['button']['registration']['contact']}</b> 📱\""
    )

    return text


async def get_text_registration_contact(
        *,
        lang: str,
) -> str:
    text = (
        f"<b>{connector[lang]['message']['registration']['contact']['greeting']}</b> 🎉\n\n"
        f"<i>{connector[lang]['message']['registration']['contact']['success']}!</i>\n\n"
    )

    return text


async def get_text_registration_support(
        *,
        lang: str,
) -> str:
    text = (
        f"⚙️ {connector[lang]['message']['registration']['contact']['support']}"
    )

    return text


async def get_text_registration_channel(
        *,
        lang: str,
) -> str:
    text = f"📺 {connector[lang]['message']['registration']['contact']['channel']}"

    return text


async def get_text_menu_main(
        *,
        lang: str,
        blocked: bool,
):
    text = (
        f"{'⚠️' if blocked else '🧭'} "
        f"<b>{connector[lang]['message']['menu']['caption']['blocked' if blocked else 'actived']}</b>"
    )

    return text


async def get_text_menu_catalog(
        *,
        lang: str,
):
    text = f"⬇️ <b>{connector[lang]['message']['menu']['catalog']}</b>"

    return text


async def get_text_menu_subcatalog(
        *,
        lang: str,
):
    text = f"⬇️ <b>{connector[lang]['message']['menu']['subcatalog']}</b>"

    return text


async def get_text_vacancy_create(
        *,
        lang: str,
        func_name: str,
        change: bool | None = None,
        text: str | None = None,
) -> str:
    if func_name == 'cancel':
        if change:
            text = f"❌ <b>{connector[lang]['message']['vacancy'][func_name]['change']}</b>"
        else:
            text = f"❌ <b>{connector[lang]['message']['vacancy'][func_name]['create']}</b>"
    elif func_name == 'change':
        if change:
            text = f"✅ <b>{connector[lang]['message']['vacancy']['finish'][func_name]}</b>"
        else:
            text = f"❎ <b>{connector[lang]['message']['vacancy']['finish']['nochange']}</b>"
    elif func_name == 'create':
        text = (
            f"✅ {connector[lang]['message']['vacancy']['finish'][func_name]['caption']}\n\n"
            f"<blockquote>❕ {connector[lang]['message']['vacancy']['finish'][func_name]['note']}</blockquote>"
        )
    else:
        func_list = [
            'catalog', 'subcatalog', 'name', 'description', 'requirement', 'employment', 'experience',
            'schedule', 'remote', 'language', 'foreigner', 'disability', 'salary', 'region', 'city',
        ]

        for key in func_list:
            if key == func_name:
                text = (
                    f"➡️ <b>{connector[lang]['message']['vacancy'][func_name]['caption']}</b>\n\n"
                    f"<i>{connector[lang]['message']['vacancy'][func_name]['note']}</i>"
                )

        if change:
            text += (
                f"\n\n📌 {connector[lang]['message']['vacancy']['skip']} "
                f"\"<b>{connector[lang]['button']['vacancy']['nochange']}</b>\"."
            )

    return text


async def get_text_vacancy_show(
        *,
        session: AsyncSession,
        lang: str,
        vacancy_id: int,
        preview: str,
        complaint: bool = False,
        city: City | None = None
) -> str:
    vacancy = await get_vacancy_preview(session=session, vacancy_id=vacancy_id)

    if vacancy.city_id:
        city = await get_city_one(session=session, city_id=vacancy.city_id)

    text = f"{'⚠️' if complaint else vacancy.catalog.logo} <b>{vacancy.name}</b>\n\n"

    if preview == 'full':
        text += (
            f"📝 <b>{connector[lang]['message']['show']['description']}:</b>\n{vacancy.description}\n\n"
            f"🎯 <b>{connector[lang]['message']['show']['requirement']}:</b>\n{vacancy.requirement}\n\n"
        )

    if vacancy.employment:
        employment = connector[lang]['message']['show']['employment']['complete']
    else:
        employment = connector[lang]['message']['show']['employment']['incomplete']

    if vacancy.experience:
        experience = connector[lang]['message']['show']['experience']['yes']
    else:
        experience = connector[lang]['message']['show']['experience']['not']

    if vacancy.schedule:
        schedule = connector[lang]['message']['show']['schedule']['stable']
    else:
        schedule = connector[lang]['message']['show']['schedule']['flexible']

    text += (
        f"🧩 <b>{connector[lang]['message']['show']['employment']['caption']}:</b>  {employment}\n"
        f"🕐 <b>{connector[lang]['message']['show']['schedule']['caption']}:</b>  {schedule}\n"
        f"💼 <b>{connector[lang]['message']['show']['experience']['caption']}:</b>  {experience}\n"
    )

    if vacancy.remote or vacancy.language or vacancy.foreigner or vacancy.disability:
        text += "\n"

        if vacancy.remote:
            text += f"✅ {connector[lang]['message']['show']['remote']}\n"

        if vacancy.language:
            text += f"✅ {connector[lang]['message']['show']['language']}\n"

        if vacancy.foreigner:
            text += f"✅ {connector[lang]['message']['show']['foreigner']}\n"

        if vacancy.disability:
            text += f"✅ {connector[lang]['message']['show']['disability']}\n"

    text += (
        f"\n<b>💰 {connector[lang]['message']['show']['salary']}:  "
        f"{vacancy.salary} {vacancy.currency.abbreviation}</b>\n\n"
    )

    if preview == 'full':
        text += (
            f"☎️ <b>{connector[lang]['message']['show']['user']['caption']}:</b>\n"
            f"{vacancy.user.first_name}  /  +{vacancy.user.phone_number}\n\n"
        )

    text += (
        f"🗺 <b>{connector[lang]['country'][vacancy.country.name]['region'][vacancy.region.name]['name']} "
        f"{connector[lang]['message']['show']['location']['region']}</b>"
    )

    if city:
        text += f"<b>  /  {connector[lang]['country'][vacancy.country.name]['region'][vacancy.region.name]['city'][city.name]}</b>"

    return text


async def get_text_vacancy_none(
        *,
        lang: str,
        view: str,
):
    text = f"❎ <b>{connector[lang]['message']['menu'][view]}</b>"

    return text


async def get_text_profile_info(
        *,
        session: AsyncSession,
        lang: str,
        user_id: int,
) -> str:
    user = await user_profile(session=session, user_id=user_id)
    vacancy = await get_vacancy_user(session=session, user_id=user_id)

    text = f"🧑‍💻 <b>{connector[lang]['message']['profile']['caption']}</b>\n\n<b># {user.username}</b>\n\n"

    if user.first_name:
        text += f"<i>{connector[lang]['message']['profile']['name']}:</i>  {user.first_name}\n"

    text += (
        f"<i>{connector[lang]['message']['profile']['phone']}:</i>  +{user.phone_number}\n"
        f"<i>{connector[lang]['message']['profile']['country']}:</i>  "
        f"{user.country.flag} {connector[lang]['country'][user.country.name]['name']}\n\n"
        f"<i>{connector[lang]['message']['profile']['language']}:</i>  {user.language.flag} {user.language.title}\n\n"
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
            f"<i>{connector[lang]['message']['profile']['vacancy']['has']['activate']}:</i>  <b>{activate}</b>\n"
            f"<i>{connector[lang]['message']['profile']['vacancy']['has']['deactivate']}:</i>  <b>{deactivate}</b>\n\n"
        )
    else:
        text += f"❎ <b>{connector[lang]['message']['profile']['vacancy']['not']}</b>\n\n"

    text += (
        f"<i>{connector[lang]['message']['profile']['date']}:</i>  "
        f"{'0' + str(user.created.day) if len(str(user.created.day)) == 1 else user.created.day}."
        f"{'0' + str(user.created.month) if len(str(user.created.month)) == 1 else user.created.month}."
        f"{user.created.year}"
    )

    return text


async def get_text_profile_settings(
        *,
        lang: str,
):
    text = f"⚙️ <b>{connector[lang]['message']['profile']['settings']}</b>\n\n"

    return text


async def get_text_settings_name(
        *,
        lang: str,
        func_name: str,
        change: bool | None = None,
        data: str | None = None,
) -> str:
    if func_name == 'cancel':
        if change:
            text = f"❌ <b>{connector[lang]['message']['settings']['cancel']['change']}</b>"
        else:
            text = f"❌ <b>{connector[lang]['message']['settings']['cancel']['create']}</b>"
    elif func_name == 'finish':
        if change:
            text = f"✅ <b>{connector[lang]['message']['settings']['finish']['change']}</b>"
        else:
            text = f"❎ <b>{connector[lang]['message']['settings']['finish']['nochange']}</b>"
    else:
        text = (
            f"➡️ <b>{connector[lang]['message']['settings'][data]['caption']}</b>\n\n"
            f"<i>{connector[lang]['message']['settings'][data]['note']}</i>"
        )

    return text


async def get_text_about_info(
        *,
        lang: str,
):
    text = (
        f"🧑‍💻 <b>{connector[lang]['message']['about']['info']['intro']['caption']}?</b>\n"
        f"{connector[lang]['message']['about']['info']['intro']['note']}\n\n"
        f"<blockquote><b>{connector[lang]['message']['about']['info']['social']['instagram']['caption']}: "
        f"{connector[lang]['message']['about']['info']['social']['instagram']['address']}</b></blockquote>\n\n"
        f"💡 <b>{connector[lang]['message']['about']['info']['problem']['caption']}?</b>\n"
        f"{connector[lang]['message']['about']['info']['problem']['note']}\n\n"
        f"💭 <b>{connector[lang]['message']['about']['info']['sense']['caption']}?</b>\n"
        f"{connector[lang]['message']['about']['info']['sense']['note']}\n\n"
        f"🤔 <b>{connector[lang]['message']['about']['info']['plan']['caption']}?</b>\n"
        f"{connector[lang]['message']['about']['info']['plan']['note']}\n\n"
    )

    return text


async def get_text_about_donate(
        *,
        lang: str,
):
    text = (
        f"💰 <b>{connector[lang]['message']['about']['donate']['caption']}</b>\n\n"
        f"<i>{connector[lang]['message']['about']['donate']['note']}</i>\n\n"
        f"💳 <code><b>{credit_cart}</b></code>"
    )

    return text


async def get_text_menu_confirm(
        *,
        lang: str,
        func_name: str,
        method: str,
        first_name: bool | None = None,
):
    if func_name == 'confirm_user':
        if method == 'create' and not first_name:
            text = f"⚠️ <b>{connector[lang]['message']['confirm'][func_name][method]['first_name']}!</b>"
        else:
            text = f"{connector[lang]['message']['confirm'][func_name][method]}?"
    else:
        text = f"{connector[lang]['message']['confirm'][func_name][method]}?"

    return text


async def get_text_menu_admin(
        *,
        lang: str,
):
    text = f"🔐 <b>{connector[lang]['message']['menu']['admin']}</b>"

    return text


async def get_text_vacancy_method(
        *,
        lang: str,
        func_name: str,
        method: str | None = None,
):
    if func_name == 'show':
        text = connector[lang]['message']['callback'][func_name][method]
    elif func_name == 'complaint':
        text = connector[lang]['message']['callback'][func_name]['create']
    else:
        text = connector[lang]['message']['callback'][func_name]

    return text


async def get_text_vacancy_favorite(
        *,
        lang: str,
        func_name: str,
        method: str,
):
    text = connector[lang]['message']['callback'][func_name][method]

    return text


async def get_text_vacancy_complaint(
        *,
        lang: str,
):
    text = f"⚠️ {connector[lang]['message']['vacancy']['blocked']}"

    return text


async def get_text_vacancy_moderation(
        *,
        lang: str,
        method: str,
):
    text = (
        f"{'✅' if method == 'activate' else '⚠️'} "
        f"<b>{connector[lang]['message']['moderation'][method]['caption']}</b>\n\n"
        f"<i>{connector[lang]['message']['moderation'][method]['info']}</i>"
    )

    return text


async def get_text_scheduler_vacancy(
        *,
        lang: str,
):
    text = f"🥺 {connector[lang]['message']['vacancy']['deactivate']}"

    return text


async def get_text_scheduler_post(
        *,
        lang: str,
):
    text = (
        f"🤖 <b>{connector[lang]['message']['post']['bot']['caption']}</b>\n"
        f"{connector[lang]['message']['post']['bot']['note']}\n\n"
        f"💬 <b>{connector[lang]['message']['post']['chat']['caption']}</b>\n"
        f"{connector[lang]['message']['post']['chat']['note']}\n\n"
        f"<blockquote>💰 <b>{connector[lang]['message']['about']['donate']['caption']}</b>\n"
        f"<i>{connector[lang]['message']['about']['donate']['note']}</i>\n\n"
        f"💳 <code><b>{credit_cart}</b></code></blockquote>"
    )

    return text
