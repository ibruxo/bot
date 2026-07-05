"""
Common interface every messenger adapter implements, plus a normalized
message shape so bot.py's command handling doesn't need to know which
platform a message came from.

Note on chat_id types: Bale/Telegram/Eitaa use numeric chat ids; Rubika
uses opaque GUID-like strings (e.g. "b0QFt...""). To keep one interface
across all four, chat_id is always a `str` here — Bale/Telegram/Eitaa
adapters just stringify their numeric ids.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class NormalizedMessage:
    platform: str
    chat_id: str
    chat_type: str  # "private" / "group" / "channel"
    text: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    title: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class MessengerAdapter:
    """Base class for a platform integration. Subclasses must set
    `platform` and implement `send_message`. `get_updates` only needs to
    be implemented by platforms that support inbound polling."""

    platform: str = "base"
    supports_polling: bool = False

    def get_updates(self) -> List[NormalizedMessage]:
        return []

    def send_message(self, chat_id: str, text: str, **kwargs) -> bool:
        raise NotImplementedError
