# 📖 Natiq Quran Bot

A Bale bot that delivers Quran verses (Arabic + Persian translation) to
users, groups, and channels — on demand and on a daily schedule.

---

## ⚠️ One thing to verify before running

The verse ingestion client (`services/quran_api_client.py`) is built
against the **documented endpoint names** of the Natiq Quran API
(`/surahs/`, `/ayahs/`, `/ayah-translations/`), but I could not confirm
the exact **response field names** — `api.natiq.ir`'s Swagger UI blocks
automated fetching.

The client already tries several likely field-name variants for each
value it reads. If ingestion logs `"Skipped N ayah(s) missing required
fields"` or comes back empty:

1. Open `https://api.natiq.ir/api/schema/swagger-ui/` in your browser
2. Try `GET /ayahs/` and `GET /ayah-translations/`, look at one real item
3. Update the candidate key names in the `_pick(...)` calls in
   `services/quran_api_client.py` — that's the only file this affects

---

## Architecture

```
   Natiq Quran API
         │
         ▼
 VerseIngestionService
         │
         ▼
    PostgreSQL  ──────►  Redis
 (source of truth)     (cache + rate limiting)
         │                    │
         └─────────┬──────────┘
                    ▼
                Bale Bot
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      Users      Groups     Channels
```

- **Postgres** is the source of truth for users, groups, channels, verses,
  admins, and delivery history (`sent_messages`).
- **Redis** is only a cache: a fast random-access copy of verses, plus
  rate-limit counters. It's never the only place data lives.
- Every incoming message registers its chat (user/group/channel) in
  Postgres, so scheduled broadcasts grow with real bot usage instead of
  relying only on a static env var list.

## Project structure

```
.
├── bot.py                        # Bale polling loop + command handlers
├── scheduler.py                  # Daily broadcasts + periodic verse refresh
├── config.py
│
├── db/
│   ├── base.py                   # SQLAlchemy declarative base
│   ├── session.py                # Engine + get_session() context manager
│   ├── models/                   # User, Channel, Group, Verse, SentMessage, BotState
│   └── repositories/             # CRUD access per model
│
├── cache/                        # Redis (named `cache`, not `redis` —
│   ├── client.py                 # see note below)
│   ├── verse_cache.py
│   └── rate_limiter.py
│
├── services/
│   ├── quran_api_client.py       # Talks to api.natiq.ir
│   ├── verse_ingestion_service.py# API -> Postgres -> Redis
│   ├── verse_service.py          # get_random_verse() + format_verse()
│   ├── user_service.py           # registers chats, admin bootstrap, stats
│   └── broadcast_service.py      # send-and-log for scheduled jobs
│
├── scripts/
│   └── ingest_verses.py          # `python -m scripts.ingest_verses`
│
├── migrations/                   # Alembic
├── Dockerfile / docker-compose.yml
└── requirements.txt
```

> **Why `cache/` and not `redis/`?** The original project had a local
> `redis/` folder, which shadowed the real `redis` pip package and broke
> every `import redis` in the project. Keep this folder named `cache`.

## Installation

```bash
git clone <your-repo-url>
cd bot
cp .env.example .env   # fill in BALE_BOT_TOKEN, TRANSLATOR_UUID, etc.
```

## Running with Docker (recommended)

```bash
docker compose build
docker compose up -d
```

Migrations run automatically on container start (see `entrypoint.sh`).
Verses are ingested automatically on first startup if Postgres is empty
(`INGEST_ON_STARTUP=true`).

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head
python -m scripts.ingest_verses   # first-time verse import
python bot.py
```

## Admin commands

Set `ADMIN_USER_IDS` in `.env` (comma-separated Bale user ids). On
startup those users are promoted to admin in Postgres. Admins can run:

- `/stats` — user/group/channel counts

## Configuration reference

See `.env.example` for the full list. Notable ones:

| Variable | Purpose |
|---|---|
| `TRANSLATOR_UUID` | Which Persian translation to ingest |
| `VERSE_REFRESH_INTERVAL_HOURS` | How often verses are re-pulled from the API |
| `RATE_LIMIT_MAX_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS` | `/random` rate limiting |
| `CHANNEL_IDS` / `GROUP_IDS` / `USER_IDS` | One-time seed data imported into Postgres on first startup |

## Database migrations

```bash
# after changing a model in db/models/
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## License

Developed by the **Natiq Foundation**. All rights reserved.
