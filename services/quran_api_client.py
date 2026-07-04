"""
Client for the Natiq Quran API (https://api.natiq.ir).

IMPORTANT — READ THIS FIRST
----------------------------
I built this against the *documented endpoint names* of the open-source
Natiq Quran API (natiq-foundation/quran-api): /surahs/, /ayahs/,
/ayah-translations/, /mushafs/, /translations/. Their exact response
*field names* are not publicly reachable (the Swagger UI blocks
automated fetching), so I could not confirm them against your live
schema.

Every place below that reads a field from the API response goes through
a small "pick first matching key" helper (`_pick`), with a short list of
likely key names. If a request stops finding data, open
https://api.natiq.ir/api/schema/swagger-ui/ in your browser, look at one
real response, and update the candidate lists in `_pick(...)` calls
below to match. That is the ONLY place you should need to touch.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from config import Config

logger = logging.getLogger(__name__)


def _pick(item: Dict[str, Any], *candidates: str, default: Any = None) -> Any:
    """Return the first present key from `candidates`, else `default`."""
    for key in candidates:
        if key in item and item[key] is not None:
            return item[key]
    return default


class QuranApiClient:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        self.base_url = (base_url or Config.QURAN_API_URL).rstrip("/")
        self.timeout = timeout

    # -------------------------
    # Generic paginated GET
    # -------------------------
    def _get_all_pages(self, path: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Walk a DRF-style paginated endpoint (`count` / `next` / `results`)
        and return every item across all pages.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        items: List[Dict[str, Any]] = []
        page = 1

        while True:
            query = {**params, "page": page, "page_size": Config.PAGE_SIZE}

            response = requests.get(url, params=query, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # Support both DRF-paginated ({"results": [...]}) and plain
            # list responses, since we couldn't confirm which this API uses.
            page_items = data.get("results", data) if isinstance(data, dict) else data

            if not page_items:
                break

            items.extend(page_items)

            has_next = bool(data.get("next")) if isinstance(data, dict) else False
            if not has_next:
                break

            page += 1

        return items

    # -------------------------
    # Surahs
    # -------------------------
    def fetch_surah_names(self) -> Dict[Any, str]:
        """Return {surah_id_or_number: surah_name}."""
        raw_surahs = self._get_all_pages("surahs/", {})

        surah_names: Dict[Any, str] = {}
        for item in raw_surahs:
            key = _pick(item, "id", "number", "surah_number")
            name = _pick(item, "name", "arabic_name", "translit_name", default="")
            if key is not None:
                surah_names[key] = name

        return surah_names

    # -------------------------
    # Ayahs (Arabic text)
    # -------------------------
    def fetch_ayahs(self, mushaf: str) -> List[Dict[str, Any]]:
        """
        Return normalized ayah dicts:
        {id, surah_key, surah_number, verse_number, verse_text, period}
        """
        raw_ayahs = self._get_all_pages("ayahs/", {"mushaf": mushaf})
        surah_names = self.fetch_surah_names()

        normalized = []
        for item in raw_ayahs:
            ayah_id = _pick(item, "id", "uuid")
            surah_key = _pick(item, "surah", "surah_id", "chapter", "chapter_id")
            surah_number = _pick(item, "surah_number", "chapter_number", default=surah_key)
            verse_number = _pick(item, "number", "ayah_number", "verse_number")
            verse_text = _pick(item, "text", "text_simple", "verse_text", default="")

            is_makki = _pick(item, "is_makki", "is_meccan")
            period_raw = _pick(item, "period", "type")
            if period_raw:
                period = str(period_raw).lower()
            elif is_makki is True:
                period = "makki"
            elif is_makki is False:
                period = "madani"
            else:
                period = ""

            normalized.append({
                "id": ayah_id,
                "surah_number": surah_number,
                "surah_name": surah_names.get(surah_key, ""),
                "verse_number": verse_number,
                "verse_text": verse_text,
                "period": period,
            })

        return normalized

    # -------------------------
    # Translations
    # -------------------------
    def fetch_translations(self, translator_uuid: str) -> Dict[Any, str]:
        """Return {ayah_id: translation_text} for the given translator."""
        raw_translations = self._get_all_pages(
            "ayah-translations/", {"translator": translator_uuid}
        )

        translations: Dict[Any, str] = {}
        for item in raw_translations:
            ayah_key = _pick(item, "ayah", "ayah_id", "verse", "verse_id")
            text = _pick(item, "text", "translation", "translation_text", default="")
            if ayah_key is not None:
                translations[ayah_key] = text

        return translations

    # -------------------------
    # Combined fetch used by the ingestion service
    # -------------------------
    def fetch_all_verses(self, mushaf: str, translator_uuid: str) -> List[Dict[str, Any]]:
        ayahs = self.fetch_ayahs(mushaf)
        translations = self.fetch_translations(translator_uuid)

        verses = []
        skipped = 0

        for ayah in ayahs:
            translation = translations.get(ayah["id"], "")

            if not ayah["verse_text"] or ayah["surah_number"] is None or ayah["verse_number"] is None:
                skipped += 1
                continue

            verses.append({
                "external_id": str(ayah["id"]) if ayah["id"] is not None else None,
                "mushaf": mushaf,
                "translator_uuid": translator_uuid,
                "surah_number": int(ayah["surah_number"]),
                "surah_name": ayah["surah_name"],
                "verse_number": int(ayah["verse_number"]),
                "verse_text": ayah["verse_text"],
                "translation": translation,
                "period": ayah["period"],
            })

        if skipped:
            logger.warning(f"Skipped {skipped} ayah(s) missing required fields")

        return verses
