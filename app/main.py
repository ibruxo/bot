import asyncio
import logging

import httpx

from app.bot.application import create_application
from app.core.config import get_settings
from app.core.container import Container
from app.core.logging import configure_logging


logger = logging.getLogger(__name__)


async def check_bot_api(
    url: str,
) -> None:
    """
    Telegram API health check.

    This must never stop the bot.
    """

    try:

        timeout = httpx.Timeout(
            connect=10.0,
            read=10.0,
            write=10.0,
            pool=10.0,
        )


        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        ) as client:


            response = await client.get(
                url
            )


        logger.info(
            "Bot API reachable (%s): %s",
            response.status_code,
            url,
        )


    except Exception as exc:

        logger.warning(
            "Bot API health check failed: %s",
            exc,
        )



async def main():

    configure_logging()


    settings = get_settings()


    logger.info(
        "Starting Quran Bot..."
    )


    container = Container()

    application = None


    try:

        #
        # Initialize services
        #

        await container.startup()


        logger.info(
            "All services initialized."
        )



        #
        # Verify Telegram API
        #

        await check_bot_api(
            settings.BOT_API
        )



        #
        # Create Telegram application
        #

        application = create_application(
            container
        )


        logger.info(
            "Initializing Telegram application..."
        )


        await application.initialize()



        logger.info(
            "Starting Telegram application..."
        )


        await application.start()



        if application.updater is None:

            raise RuntimeError(
                "Updater is not available."
            )



        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=None,
        )


        logger.info(
            "Bot is now polling."
        )



        while True:

            await asyncio.sleep(
                3600
            )



    except KeyboardInterrupt:

        logger.info(
            "Stopping bot..."
        )


    except Exception:

        logger.exception(
            "Fatal bot error"
        )


    finally:


        try:

            if application is not None:


                if application.updater is not None:

                    await application.updater.stop()



                await application.stop()

                await application.shutdown()



        except Exception:

            logger.exception(
                "Error shutting down Telegram application"
            )



        finally:

            await container.shutdown()



        logger.info(
            "Shutdown complete."
        )



if __name__ == "__main__":

    asyncio.run(
        main()
    )
