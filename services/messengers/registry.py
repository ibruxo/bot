import logging
from typing import Dict

from config import Config
from services.messengers.bale import BaleAdapter
from services.messengers.base import MessengerAdapter
from services.messengers.eitaa import EitaaAdapter
from services.messengers.rubika import RubikaAdapter
from services.messengers.telegram import TelegramAdapter

logger = logging.getLogger(__name__)

_ADAPTER_CLASSES = {
    "bale": BaleAdapter,
    "telegram": TelegramAdapter,
    "eitaa": EitaaAdapter,
    "rubika": RubikaAdapter,
}


def build_adapters() -> Dict[str, MessengerAdapter]:
    """
    Build one adapter per platform listed in ENABLED_PLATFORMS that also
    has a token configured. Returns {platform_name: adapter_instance}.
    """
    adapters: Dict[str, MessengerAdapter] = {}

    for platform in Config.get_enabled_platforms():
        token = Config.get_platform_token(platform)

        if not token:
            logger.warning(f"'{platform}' is enabled but has no token configured — skipping")
            continue

        adapter_cls = _ADAPTER_CLASSES.get(platform)
        if not adapter_cls:
            logger.warning(f"Unknown platform '{platform}' in ENABLED_PLATFORMS — skipping")
            continue

        adapters[platform] = adapter_cls(token)
        logger.info(f"✅ {platform} adapter ready")

    if not adapters:
        logger.warning("No messenger platforms configured — the bot has nothing to talk to")

    return adapters
