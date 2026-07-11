from __future__ import annotations

import logging
import random
from typing import Any

from app.api.client import APIClient
from app.cache.quran import QuranCache
from app.schemas.ayah import Ayah


logger = logging.getLogger(__name__)


class NatiqProvider:

    def __init__(
        self,
        client: APIClient,
        cache: QuranCache,
    ) -> None:

        self._client = client
        self._cache = cache


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


    async def list_ayahs(
        self,
    ) -> list[dict[str, Any]]:
        """
        Load ayahs from API.

        Keeps partial results if API fails.
        """

        results: list[dict[str, Any]] = []

        page = 1


        while True:

            try:

                response = await self._client.get(
                    "/ayahs/",
                    params={
                        "page": page,
                    },
                )


                items = self._extract_list(
                    response.json()
                )


            except Exception as exc:

                logger.warning(
                    "Stopped loading ayahs at page %s: %s",
                    page,
                    exc,
                )

                break



            if not items:
                break



            results.extend(
                items
            )


            logger.info(
                "Loaded %s ayahs",
                len(results),
            )



            if len(items) < 200:
                break



            page += 1



        return results



    async def list_surahs(
        self,
    ) -> list[dict[str, Any]]:
        """
        Surahs are extracted from ayahs.
        """

        return []



    async def list_translations(
        self,
    ) -> list[dict[str, Any]]:
        """
        Disabled.

        Translation endpoint is not required.
        """

        return []



    async def list_takhtits(
        self,
    ) -> list[dict[str, Any]]:

        try:

            response = await self._client.get(
                "/takhtits/",
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



    async def random_ayah(
        self,
    ) -> Ayah:


        if not self._cache.ayahs:

            raise RuntimeError(
                "Quran cache not initialized"
            )



        data = random.choice(
            self._cache.ayahs
        )



        surah = data.get(
            "surah",
            {},
        )



        names = (
            surah.get("names")
            or []
        )



        surah_name = "Unknown"



        if names:

            first = names[0]

            if isinstance(first, dict):

                surah_name = (
                    first.get("name")
                    or "Unknown"
                )



        return Ayah.parse_obj(
            {
                "text": data["text"],

                "surah_name": surah_name,

                "surah_number": (
                    surah.get("number")
                    or 0
                ),

                "ayah_number": data["number"],
            }
        )
