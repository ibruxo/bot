from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.api.checker import APIFeatureChecker, MessengerFeature


_feature_checker = APIFeatureChecker()


def random_ayah_keyboard(
    ayah_uuid: str | None = None,
) -> InlineKeyboardMarkup | None:

    if not _feature_checker.log_if_unsupported(
        MessengerFeature.INLINE_KEYBOARD,
        context="random_ayah_keyboard",
    ):
        return None

    if not _feature_checker.log_if_unsupported(
        MessengerFeature.CALLBACK_QUERY,
        context="random_ayah_keyboard",
    ):
        return None

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="آیه بعدی ➡️",
                    callback_data=f"next_ayah:{ayah_uuid}"
                    if ayah_uuid
                    else "next_ayah",
                ),
            ]
        ]
    )
