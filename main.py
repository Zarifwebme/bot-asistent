import asyncio
import logging

from services.telegram_client import start_client


logger = logging.getLogger(__name__)


async def main():
    await start_client()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print("\n🛑 Dastur foydalanuvchi tomonidan to'xtatildi.")

    except Exception as error:

        logger.critical(
            "💥 Dastur to'xtadi: %s: %s",
            type(error).__name__,
            error,
        )