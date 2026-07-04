from redis import Redis
from redis.verses import VerseRepository


class VerseService:
    def __init__(self, redis: Redis):
        self.repo = VerseRepository(redis)

    def get_random_verse(self):
        return self.repo.get_random()

    def format_verse(self, data: dict, config):
        period = data.get("period", "")

        icon = "🕋" if period == "makki" else "🕌" if period == "madani" else "📖"

        return (
            f"{icon} *سوره {data['surah_name']}*\n\n"
            f"📖 *{data['verse_text']} ﴿{data['verse_number']}﴾*\n\n"
            f"📝 {data['translation']}\n"
        )
