from environs import Env

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from .schedulers import scheduler_add


def telegram_env(path: str):
    env = Env()
    env.read_env(path)

    return env.str("BOT_TOKEN"), env.int("BOT_ADMIN")


def postgres_env(path: str):
    env = Env()
    env.read_env(path)

    return {
        'db_name': env.str("POSTGRES_NAME"),
        'db_user': env.str("POSTGRES_USER"),
        'db_pass': env.str("POSTGRES_PASS"),
        'db_host': env.str("POSTGRES_HOST"),
    }


def redis_env(path: str):
    env = Env()
    env.read_env(path)

    return {
        'db_name': env.str("REDIS_NAME"),
        'db_host': env.str("REDIS_HOST"),
        'db_port': env.str("REDIS_PORT"),
    }


def scheduler_env(path: str):
    env = Env()
    env.read_env(path)

    return {
        'db_name': env.str("SCHEDULER_NAME"),
        'db_host': env.str("SCHEDULER_HOST"),
        'db_port': env.str("SCHEDULER_PORT"),
    }


token, admin = telegram_env('.env')
postgres = postgres_env('.env')
redis = redis_env('.env')
scheduler = scheduler_env('.env')


# Time Tasks
def scheduler_tasks():
    return ContextSchedulerDecorator(AsyncIOScheduler(
        timezone="Europe/Kiev",
        jobstores={
            'default': RedisJobStore(
                jobs_key='dispatched_trips_jobs',
                run_times_key='dispatched_trips_running',
                db=scheduler['db_name'],
                host=scheduler['db_host'],
                port=scheduler['db_port']
            )
        }
    ))


PostgresURL = f"postgresql+asyncpg://{postgres['db_user']}:{postgres['db_pass']}@{postgres['db_host']}/{postgres['db_name']}"
async_engine = create_async_engine(PostgresURL, echo=True)
session_maker = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

bot = Bot(token=token, parse_mode='HTML')

storage = RedisStorage.from_url(f"{redis['db_name']}://{redis['db_host']}:{redis['db_port']}/0")

schedulers = scheduler_add(scheduler_tasks())
