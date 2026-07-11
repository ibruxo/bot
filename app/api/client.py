from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class APIClient:

    def __init__(self) -> None:

        settings = get_settings()

        self._client = httpx.AsyncClient(
            base_url=settings.NATIQ_PRIMARY_API.rstrip("/"),
            timeout=httpx.Timeout(
                connect=15.0,
                read=45.0,
                write=30.0,
                pool=15.0,
            ),
            headers={
                "Accept": "application/json",
            },
        )

        if settings.NATIQ_API_TOKEN:
            self._client.headers["Authorization"] = (
                f"Token {settings.NATIQ_API_TOKEN}"
            )


    async def connect(self) -> None:
        logger.info(
            "HTTP client initialized."
        )


    async def close(self) -> None:

        await self._client.aclose()

        logger.info(
            "HTTP client closed."
        )


    async def get(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:

        retries = 3

        for attempt in range(retries):

            try:

                response = await self._client.get(
                    url,
                    **kwargs,
                )

                response.raise_for_status()

                return response


            except (
                httpx.ReadTimeout,
                httpx.ConnectTimeout,
                httpx.ConnectError,
            ) as exc:

                if attempt == retries - 1:
                    logger.error(
                        "GET failed after retries: %s",
                        exc,
                    )
                    raise


                delay = 2 ** attempt

                logger.warning(
                    "GET timeout. Retrying in %ss",
                    delay,
                )

                await asyncio.sleep(delay)



    async def post(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:

        response = await self._client.post(
            url,
            **kwargs,
        )

        response.raise_for_status()

        return response



    async def put(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:

        response = await self._client.put(
            url,
            **kwargs,
        )

        response.raise_for_status()

        return response



    async def patch(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:

        response = await self._client.patch(
            url,
            **kwargs,
        )

        response.raise_for_status()

        return response



    async def delete(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:

        response = await self._client.delete(
            url,
            **kwargs,
        )

        response.raise_for_status()

        return response
