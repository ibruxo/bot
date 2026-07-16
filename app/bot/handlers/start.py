from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from app.bot.guards.rate_limit import RateLimitRule, rate_limit


logger = logging.getLogger(__name__)



@rate_limit(
    RateLimitRule(
        limit=3,
        window_seconds=10,
    )
)
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not update.message:
        return


    await update.message.reply_text(
        "بسم الله الرحمن الرحیم\n\n"
        "ربات قرآن ناطق آماده است.\n\n"
        "برای دریافت آیه تصادفی از دستور /random استفاده کنید."
    )



def get_handler() -> CommandHandler:

    return CommandHandler(
        "start",
        start,
    )
