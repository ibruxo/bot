"""
Rubika Bot Platform API (confirmed from rubika.ir/botapi and
rubika.ir/botapi/methods): every call is a POST to
`https://botapi.rubika.ir/v3/{token}/{method}` with a JSON body.

Confirmed shapes:
- sendMessage: POST body {"chat_id": ..., "text": ...} -> {"data": {...}}
- getUpdates (long polling): POST body {"limit": N}

ONE THING NOT FULLY CONFIRMED: Rubika's docs describe passing the
previous response's cursor value back in on the next getUpdates call to
avoid re-reading old messages ("start_id"), but the public examples we
could reach only showed the `limit` field, not the exact key name for
that cursor or where it appears in the response. This adapter guesses
`offset_id` / `next_offset_id` (a common naming pattern in Rubika
client libraries) — if updates repeat or the field is silently ignored,
check https://rubika.ir/botapi/methods for the real key name and adjust
the two lines marked below.

Rubika chat_id values are opaque GUID-like strings (e.g.
"b0QFt...""), unlike Bale/Telegram's numeric ids — this is why the
shared NormalizedMessage/adapter interface treats chat_id as a string
everywhere.
"""

import logging
from typing import List, Optional

import requests

from services.messengers.base import MessengerAdapter, NormalizedMessage

logger = logging.getLogger(__name__)


class RubikaAdapter(MessengerAdapter):
    platform = "rubika"
    supports_polling = True

    def __init__(self, token: str, api_base_url: str = "https://botapi.rubika.ir/v3", timeout: int = 30):
        self.api_url = f"{api_base_url}/{token}"
        self.timeout = timeout
        self._offset_id: Optional[str] = None  # see docstring above

    def _call(self, method: str, body: dict) -> dict:
        response = requests.post(f"{self.api_url}/{method}", json=body, timeout=self.timeout)
        return response.json()

    def get_updates(self) -> List[NormalizedMessage]:
        body = {"limit": 100}
        if self._offset_id:
            body["offset_id"] = self._offset_id  # ADJUST if the real field name differs

        try:
            data = self._call("getUpdates", body)
        except Exception as e:
            logger.error(f"[rubika] get_updates error: {e}")
            return []

        payload = data.get("data", data)
        raw_updates = payload.get("updates", [])

        self._offset_id = payload.get("next_offset_id", self._offset_id)  # ADJUST if needed

        messages = []
        for update in raw_updates:
            new_message = update.get("new_message") or update.get("inline_message")
            if not new_message:
                continue

            chat_id = update.get("chat_id") or new_message.get("chat_id")
            if not chat_id:
                continue

            author_type = (update.get("author_type") or "").lower()
            chat_type = {
                "group": "group",
                "channel": "channel",
            }.get(author_type, "private")

            messages.append(NormalizedMessage(
                platform=self.platform,
                chat_id=str(chat_id),
                chat_type=chat_type,
                text=new_message.get("text", ""),
                raw=update,
            ))

        return messages

    def send_message(self, chat_id: str, text: str, **kwargs) -> bool:
        try:
            data = self._call("sendMessage", {"chat_id": chat_id, "text": text})

            if data.get("status") not in (None, "OK") and not data.get("data"):
                logger.error(f"[rubika] sendMessage failed for {chat_id}: {data}")
                return False

            return True

        except Exception as e:
            logger.error(f"[rubika] send_message error for {chat_id}: {e}")
            return False
