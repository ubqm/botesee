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
CMD ["uvicorn", "bot.web.main:app", "--host", "0.0.0.0", "--port", "5000"]

FROM base as celery
ENV PYTHONPATH "${PYTHONPATH}:/app"
WORKDIR /app
CMD ["celery", "-A", "bot.celery.tasks.app", "worker", "-l", "INFO"]
