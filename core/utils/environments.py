from environs import Env


def main_envs(path: str):
    env = Env()
    env.read_env(path)

    return {
        # Telegram Bot Envs
        'bot_token': env.str("BOT_TOKEN"),
        'bot_admin': env.int("BOT_ADMIN"),
        # PostgreSQL Envs
        'db_name': env.str("POSTGRES_DB"),
        'db_user': env.str("POSTGRES_USER"),
        'db_pass': env.str("POSTGRES_PASSWORD"),
        'db_host': env.str("POSTGRES_HOST"),
    }


envs = main_envs('.env')
