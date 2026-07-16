from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class QuranCache:
    """
    In-memory Quran cache.

    Stores both raw collections and lookup dictionaries so
    the provider never has to iterate over thousands of items
    for every random ayah.
    """

    def __init__(self) -> None:

        # Raw data

        self.ayahs: list[dict[str, Any]] = []
        self.takhtits: list[dict[str, Any]] = []
        self.translations: list[dict[str, Any]] = []
        self.surahs: list[dict[str, Any]] = []

        # Lookup tables

        self.ayah_map: dict[str, dict[str, Any]] = {}

        self.takhtit_map: dict[str, dict[str, Any]] = {}

        self.translation_map: dict[str, dict[str, Any]] = {}

        self.surah_map: dict[int, dict[str, Any]] = {}
        self.surah_uuid_map: dict[str, dict[str, Any]] = {}


    # --------------------------------------------------
    # Ayahs
    # --------------------------------------------------

    def set_ayahs(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.ayahs = items

        self.ayah_map = {
            item["uuid"]: item
            for item in items
            if item.get("uuid")
        }

        logger.info(
            "Cached %s ayahs",
            len(items),
        )


    # --------------------------------------------------
    # Takhtits
    # --------------------------------------------------

    def set_takhtits(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.takhtits = items

        self.takhtit_map = {
            item["uuid"]: item
            for item in items
            if item.get("uuid")
        }

        logger.info(
            "Cached %s takhtits",
            len(items),
        )


    # --------------------------------------------------
    # Translations
    # --------------------------------------------------

    def set_translations(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.translations = items

        self.translation_map = {
            item["ayah_uuid"]: item
            for item in items
            if item.get("ayah_uuid")
        }

        logger.info(
            "Cached %s translations",
            len(items),
        )


    # --------------------------------------------------
    # Surahs
    # --------------------------------------------------

    def set_surahs(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.surahs = items

        self.surah_map = {
            item["number"]: item
            for item in items
            if item.get("number") is not None
        }

        self.surah_uuid_map = {
            item["uuid"]: item
            for item in items
            if item.get("uuid")
        }

        logger.info(
            "Cached %s surahs",
            len(items),
        )
