FROM python:3.11 AS base

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY bot /bot
ENV PYTHONPATH "${PYTHONPATH}:/"
WORKDIR /
#COPY .env .env

FROM base AS discord-bot

CMD ["python3", "bot/discord_bot/main.py"]

FROM base as web

COPY alembic.ini alembic.ini
COPY web.sh web.sh
RUN chmod +x web.sh
ENTRYPOINT ["/web.sh"]

FROM base as celery

CMD ["celery", "-A", "bot.celery.tasks.app", "worker", "-l", "INFO"]
