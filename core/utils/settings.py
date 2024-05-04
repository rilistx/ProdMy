from environs import Env

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator


def telegram_env(path: str):
    env = Env()
    env.read_env(path)

    return (
        env.str("BOT_TOKEN"),
        env.int("ID_CHANNEL_UA"),
        {
            'id': env.int("ADMIN_ID"),
            'name': env.str("ADMIN_NAME"),
            'phone': env.str("ADMIN_PHONE"),
        },
    )


def language_env(path: str):
    env = Env()
    env.read_env(path)

    return env.str("DEFAULT_LANGUAGE")


def currency_env(path: str):
    env = Env()
    env.read_env(path)

    return env.str("DEFAULT_CURRENCY")


def country_env(path: str):
    env = Env()
    env.read_env(path)

    return env.str("DEFAULT_COUNTRY")


def credit_env(path: str):
    env = Env()
    env.read_env(path)

    return env.str("CREDIT_CART")


def complaint_env(path: str):
    env = Env()
    env.read_env(path)

    return env.int("COMPLAINT_COUNT")


def postgres_env(path: str):
    env = Env()
    env.read_env(path)

    return {
        'db_name': env.str("POSTGRES_DB"),
        'db_user': env.str("POSTGRES_USER"),
        'db_pass': env.str("POSTGRES_PASSWORD"),
        'db_host': env.str("POSTGRES_HOST"),
    }


def redis_env(path: str):
    env = Env()
    env.read_env(path)

    return {
        'db_name': env.str("REDIS_NAME"),
        'db_data': env.str("REDIS_DATABASES"),
        'db_pass': env.str("REDIS_PASSWORD"),
        'db_host': env.str("REDIS_HOST"),
        'db_port': env.str("REDIS_PORT"),
    }


token, channel, admin = telegram_env('.env')

postgres = postgres_env('.env')
redis = redis_env('.env')

default_language = language_env('.env')
default_currency = currency_env('.env')
default_country = country_env('.env')

credit_cart = credit_env('.env')

complaint_limit = complaint_env('.env')


PostgresURL = f"postgresql+asyncpg://{postgres['db_user']}:{postgres['db_pass']}@{postgres['db_host']}/{postgres['db_name']}"
async_engine = create_async_engine(PostgresURL, echo=False)
async_session_maker = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


bot = Bot(token=token, parse_mode=ParseMode.HTML)
storage = RedisStorage.from_url(f"{redis['db_name']}://{redis['db_host']}:{redis['db_port']}/0")


def async_scheduler():
    connect = ContextSchedulerDecorator(AsyncIOScheduler(
        timezone="Europe/Kiev",
        jobstores={
            'default': RedisJobStore(
                jobs_key='dispatched_trips_jobs',
                run_times_key='dispatched_trips_running',
                db=4,
                host=redis['db_host'],
                port=redis['db_port'],
            )
        }
    ))

    connect.ctx.add_instance(bot, declared_class=Bot)

    return connect
