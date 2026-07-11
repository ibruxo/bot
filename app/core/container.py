from __future__ import annotations

from app.api.client import APIClient
from app.api.provider import NatiqProvider

from app.cache.quran import QuranCache
from app.cache.loader import QuranCacheLoader
from app.cache.redis import RedisCache

from app.core.config import Settings, get_settings
from app.database.session import Database


class Container:
    """
    Central dependency container.

    Creates and owns all long-running services.
    """

    def __init__(self) -> None:

        self._settings: Settings = get_settings()

        #
        # Infrastructure
        #

        self._database = Database()

        self._cache = RedisCache()

        self._http = APIClient()


        #
        # Quran cache
        #

        self._quran_cache = QuranCache()


        #
        # API provider
        #

        self._provider = NatiqProvider(
            client=self._http,
            cache=self._quran_cache,
        )


        #
        # Cache loader
        #

        self._quran_cache_loader = QuranCacheLoader(
            provider=self._provider,
            cache=self._quran_cache,
        )


    #
    # Settings
    #

    @property
    def settings(self) -> Settings:
        return self._settings


    #
    # Infrastructure
    #

    @property
    def database(self) -> Database:
        return self._database


    @property
    def cache(self) -> RedisCache:
        return self._cache


    @property
    def http(self) -> APIClient:
        return self._http


    #
    # Quran
    #

    @property
    def quran_cache(self) -> QuranCache:
        return self._quran_cache


    @property
    def quran_cache_loader(self) -> QuranCacheLoader:
        return self._quran_cache_loader


    #
    # Provider
    #

    @property
    def provider(self) -> NatiqProvider:
        return self._provider


    #
    # Lifecycle
    #

    async def startup(self) -> None:

        await self.database.connect()

        await self.cache.connect()

        await self.http.connect()

        await self.quran_cache_loader.load()


    async def shutdown(self) -> None:

        try:
            await self.http.close()

        finally:
            try:
                await self.cache.close()

            finally:
                await self.database.dispose()
