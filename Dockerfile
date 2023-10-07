FROM python:3.11 AS base

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY .env .env
COPY bot /app/bot
COPY .env /app/.env
COPY .env /app/bot/.env
COPY .env /app/bot/web/.env
COPY .env /app/bot/discord_bot/.env

WORKDIR bot

FROM base AS discord-bot
ENV PYTHONPATH "${PYTHONPATH}:/app"
WORKDIR /app
CMD ["python3", "bot/discord_bot/main.py"]


FROM base as web
ENV PYTHONPATH "${PYTHONPATH}:/app"
WORKDIR /app
COPY web.sh web.sh
COPY alembic.ini alembic.ini
RUN chmod +x web.sh
ENTRYPOINT ["/app/web.sh"]

FROM base as celery
ENV PYTHONPATH "${PYTHONPATH}:/app"
WORKDIR /app
CMD ["celery", "-A", "bot.celery.tasks.app", "worker", "-l", "INFO"]
