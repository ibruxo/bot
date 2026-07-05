"""
Eitaayar (eitaayar.ir) bot API. Confirmed from public docs
(eitaayar.ir/assets/download/API_eitaayar.ir.pdf): base URL is
`https://eitaayar.ir/api/{token}/{method}`, with `getMe`, `sendMessage`,
and `sendDocument` as the only documented methods.

There is no documented `getUpdates`/webhook mechanism for a plain
Eitaayar bot token — it's a send-only broadcast API (your bot must be
made an admin of the channel/group it posts to). So this adapter only
implements sending; `get_updates` always returns an empty list.
"""

import logging
from typing import List

import requests

from services.messengers.base import MessengerAdapter, NormalizedMessage

logger = logging.getLogger(__name__)


class EitaaAdapter(MessengerAdapter):
    platform = "eitaa"
    supports_polling = False  # send-only API, see module docstring

    def __init__(self, token: str, api_base_url: str = "https://eitaayar.ir/api", timeout: int = 30):
        self.api_url = f"{api_base_url}/{token}"
        self.timeout = timeout

    def get_updates(self) -> List[NormalizedMessage]:
        # No inbound updates mechanism for Eitaayar bot tokens.
        return []

    def send_message(self, chat_id: str, text: str, **kwargs) -> bool:
        payload = {"chat_id": chat_id, "text": text}

        try:
            response = requests.post(f"{self.api_url}/sendMessage", data=payload, timeout=self.timeout)
            data = response.json()

            if not data.get("ok"):
                logger.error(f"[eitaa] sendMessage failed for {chat_id}: {data}")
                return False

            return True

        except Exception as e:
            logger.error(f"[eitaa] send_message error for {chat_id}: {e}")
            return False
