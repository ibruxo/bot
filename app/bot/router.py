from telegram.ext import Application

from app.api.checker import APIFeatureChecker, MessengerFeature
from app.bot.handlers.start import (
    get_handler as get_start_handler,
)

from app.bot.handlers.random import (
    get_handler as get_random_handler,
)

from app.bot.handlers.callbacks import (
    get_callback_handler,
)


_feature_checker = APIFeatureChecker()


def register_handlers(
    application: Application,
) -> None:


    application.add_handler(
        get_start_handler()
    )


    application.add_handler(
        get_random_handler()
    )


    if (
        _feature_checker.supports(MessengerFeature.INLINE_KEYBOARD)
        and _feature_checker.supports(MessengerFeature.CALLBACK_QUERY)
    ):
        application.add_handler(
            get_callback_handler()
        )
