from __future__ import annotations

import logging

from app.api.provider import NatiqProvider
from app.cache.quran import QuranCache


logger = logging.getLogger(__name__)


class QuranCacheLoader:


    def __init__(
        self,
        provider: NatiqProvider,
        cache: QuranCache,
    ) -> None:

        self.provider = provider
        self.cache = cache



    async def load(
        self,
    ) -> None:

        logger.info(
            "Loading Quran cache..."
        )



        #
        # Ayahs
        #

        try:

            ayahs = await self.provider.list_ayahs()


            if ayahs:

                self.cache.ayahs.extend(
                    ayahs
                )


                for ayah in ayahs:


                    surah = ayah.get(
                        "surah"
                    )


                    if not surah:
                        continue



                    uuid = surah.get(
                        "uuid"
                    )


                    if uuid:

                        self.cache.surahs[uuid] = surah



            logger.info(
                "Cached %s ayahs",
                len(self.cache.ayahs),
            )


            logger.info(
                "Cached %s surahs",
                len(self.cache.surahs),
            )


        except Exception:

            logger.exception(
                "Failed loading ayahs"
            )



        #
        # Translations
        #

        try:

            translations = (
                await self.provider.list_translations()
            )


            self.cache.translations = translations



            logger.info(
                "Cached %s translations",
                len(translations),
            )


        except Exception:

            logger.exception(
                "Failed loading translations"
            )



        #
        # Takhtits
        #

        try:

            takhtits = (
                await self.provider.list_takhtits()
            )


            self.cache.takhtits = takhtits



            logger.info(
                "Cached %s takhtits",
                len(takhtits),
            )


        except Exception:

            logger.exception(
                "Failed loading takhtits"
            )



        logger.info(
            "Quran cache loading completed."
        )
