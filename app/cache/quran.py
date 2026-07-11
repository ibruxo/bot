from __future__ import annotations


class QuranCache:

    def __init__(self) -> None:

        self.ayahs: list = []

        self.surahs: dict = {}

        self.translations: list = []

        self.takhtits: list = []



    def get_surah(
        self,
        uuid: str | None,
    ):

        if not uuid:
            return None

        return self.surahs.get(uuid)
