# ============================================
# Stage 1: Build Stage
# ============================================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Stage 2: Runtime Stage
# ============================================
FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Riyadh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN groupadd -r quranbot && useradd -r -g quranbot quranbot

COPY --from=builder /install /usr/local

WORKDIR /app

COPY --chown=quranbot:quranbot . .
RUN chmod +x entrypoint.sh

RUN chown -R quranbot:quranbot /app

USER quranbot

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["./entrypoint.sh"]
