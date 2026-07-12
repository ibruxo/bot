from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from app.api.client import APIClient
from app.cache.quran import QuranCache
from app.core.config import get_settings
from app.schemas.ayah import Ayah

logger = logging.getLogger(__name__)


class NatiqProvider:
    """
    Provider for Natiq Quran API.

    Responsibilities:
    - Load all ayahs using offset pagination
    - Extract surahs from ayah metadata
    - Load translations when available
    - Load takhtits
    - Provide random ayahs
    """

    def __init__(
        self,
        client: APIClient,
        cache: QuranCache,
    ) -> None:

        self._client = client
        self._cache = cache
        self._settings = get_settings()

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _extract_list(
        payload: Any,
    ) -> list[dict[str, Any]]:

        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):

            return (
                payload.get("results")
                or payload.get("data")
                or []
            )

        return []

    async def _get_with_retry(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> Any:

        last_error = None

        for attempt in range(retries):

            try:

                response = await self._client.get(
                    endpoint,
                    params=params,
                )

                return response

            except Exception as exc:

                last_error = exc

                delay = 2 ** attempt

                logger.warning(
                    "Request failed %s attempt %s/%s: %s",
                    endpoint,
                    attempt + 1,
                    retries,
                    exc,
                )

                await asyncio.sleep(delay)

        raise last_error

    # ---------------------------------------------------------
    # Ayahs
    # ---------------------------------------------------------

    async def list_ayahs(
        self,
    ) -> list[dict[str, Any]]:

        logger.info(
            "Loading Quran ayahs..."
        )

        results: list[dict[str, Any]] = []

        offset = 0

        limit = 200

        mushaf = self._settings.QURAN_MUSHAF

        while True:

            response = await self._get_with_retry(
                "/ayahs/",
                params={
                    "mushaf": mushaf,
                    "offset": offset,
                },
            )

            items = self._extract_list(
                response.json()
            )

            if not items:

                break


            results.extend(items)


            logger.info(
                "Loaded %s ayahs",
                len(results),
            )


            offset += limit


        logger.info(
            "Finished loading %s ayahs",
            len(results),
        )

        return results


    # ---------------------------------------------------------
    # Surahs
    # ---------------------------------------------------------

    async def list_surahs(
        self,
    ) -> list[dict[str, Any]]:

        """
        Surahs are embedded inside ayahs.
        API /surahs/ endpoint is not used.
        """

        if not self._cache.ayahs:

            logger.warning(
                "Cannot extract surahs without ayahs"
            )

            return []


        surahs: dict[str, dict[str, Any]] = {}


        for ayah in self._cache.ayahs:

            surah = ayah.get(
                "surah"
            )

            if not surah:

                continue


            uuid = surah.get(
                "uuid"
            )

            if not uuid:

                continue


            if uuid not in surahs:

                surahs[uuid] = surah


        result = list(
            surahs.values()
        )


        result.sort(
            key=lambda x: x.get(
                "number",
                0,
            )
        )


        logger.info(
            "Extracted %s surahs",
            len(result),
        )


        return result


    # ---------------------------------------------------------
    # Translations
    # ---------------------------------------------------------

    async def list_translations(
        self,
    ) -> list[dict[str, Any]]:

        try:

            response = await self._get_with_retry(
                "/translations/",
                params={
                    "mushaf": self._settings.QURAN_MUSHAF,
                    "language": self._settings.QURAN_TRANSLATION_LANGUAGE,
                },
            )


            translations = self._extract_list(
                response.json()
            )


            if not translations:

                logger.info(
                    "No translations available"
                )

                return []


            translation = translations[0]


            uuid = (
                translation.get("uuid")
                or translation.get("id")
            )


            if not uuid:

                return []


            return await self._load_translation_ayahs(
                uuid
            )


        except Exception as exc:

            logger.warning(
                "Failed loading translations: %s",
                exc,
            )

            return []


    async def _load_translation_ayahs(
        self,
        translation_uuid: str,
    ) -> list[dict[str, Any]]:

        results = []

        offset = 0

        limit = 200


        while True:

            response = await self._get_with_retry(
                f"/translations/{translation_uuid}/ayahs/",
                params={
                    "offset": offset,
                },
            )


            items = self._extract_list(
                response.json()
            )


            if not items:

                break


            results.extend(items)


            offset += limit


        logger.info(
            "Loaded %s translations",
            len(results),
        )


        return results


    # ---------------------------------------------------------
    # Takhtits
    # ---------------------------------------------------------

    async def list_takhtits(
        self,
    ) -> list[dict[str, Any]]:

        try:

            response = await self._get_with_retry(
                "/takhtits/",
                params={
                    "mushaf": self._settings.QURAN_MUSHAF,
                },
            )


            return self._extract_list(
                response.json()
            )


        except Exception as exc:

            logger.warning(
                "Failed loading takhtits: %s",
                exc,
            )

            return []


    # ---------------------------------------------------------
    # Random Ayah
    # ---------------------------------------------------------

    async def random_ayah(
        self,
    ) -> Ayah:


        if not self._cache.ayahs:

            raise RuntimeError(
                "Quran cache is empty"
            )


        data = random.choice(
            self._cache.ayahs
        )


        surah = data.get(
            "surah",
            {},
        )


        names = surah.get(
            "names",
            [],
        )


        surah_name = "Unknown"


        if names:

            first = names[0]

            if isinstance(first, dict):

                surah_name = (
                    first.get("name")
                    or "Unknown"
                )


        translation = None


        ayah_uuid = (
            data.get("uuid")
            or data.get("id")
        )


        for item in self._cache.translations:

            if (
                item.get("ayah")
                == ayah_uuid
            ):

                translation = (
                    item.get("text")
                )

                break


        return Ayah(
            text=data.get(
                "text",
                "",
            ),
            translation=translation,
            surah_name=surah_name,
            surah_number=surah.get(
                "number",
                0,
            ),
            ayah_number=data.get(
                "number",
                0,
            ),
        )
