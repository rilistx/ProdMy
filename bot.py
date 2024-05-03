import asyncio
import logging

from core import start_polling


async def main() -> None:
    # Logging code
    logging.basicConfig(
        level=logging.INFO,
        filename="loger.log",
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Start Polling Bot
    await start_polling()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('This bot stopped 😈')
