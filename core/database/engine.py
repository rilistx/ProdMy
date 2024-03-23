from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from core.database.models import Base
from core.utils.environments import envs


DataBaseURL = f"postgresql+asyncpg://{envs['db_user']}:{envs['db_pass']}@{envs['db_host']}/{envs['db_name']}"

async_engine = create_async_engine(DataBaseURL, echo=True)
async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
