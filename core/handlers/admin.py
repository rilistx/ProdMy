from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from core.handlers.menu import redirector
from core.keyboards.menu import MenuCallBack


admin_router = Router()


@admin_router.callback_query(MenuCallBack.filter(F.key == 'moderation'))
async def catalog_vacancy_callback(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        session: AsyncSession,
) -> None:
    if callback_data.method == 'blocked':
        pass

    elif callback_data.method == 'activate':
        pass

    else:
        pass

    return await redirector(
        callback=callback,
        callback_data=callback_data,
        session=session,
        view=callback_data.view,
        level=3,
        key='view',
        page=callback_data.page - 1 if callback_data.page - 1 != 0 else 1,
        catalog_id=callback_data.catalog_id,
        subcatalog_id=callback_data.subcatalog_id,
    )
