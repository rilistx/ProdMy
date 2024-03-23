from sqlalchemy.ext.asyncio import AsyncSession


# Class Request -> CRUD (Create, Read, Update, Delete) data
class Request:
    @staticmethod
    async def create_data(async_session: AsyncSession, query):
        async with async_session as session:
            async with session.begin():
                session.add(query)

            await session.commit()

    @staticmethod
    async def read_data(async_session: AsyncSession, query):
        async with async_session as session:
            result = await session.execute(query)

        return result

    @staticmethod
    async def update_data(async_session: AsyncSession, query, **kwargs):
        async with async_session as session:
            result = await session.execute(query)
            data = result.scalars().one()
            for key, value in kwargs.items():
                setattr(data, key, value)

            await session.commit()

    @staticmethod
    async def delete_data(async_session: AsyncSession, query):
        async with async_session as session:
            async with session.begin():
                await session.delete(query)

            await session.commit()


queryset = Request()
