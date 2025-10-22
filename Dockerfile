# Stage 1: Build stage
FROM python:3.12.8-slim AS base
RUN apt-get update
RUN apt-get install build-essential curl -y

RUN pip install -U pip setuptools wheel
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

COPY pyproject.toml uv.lock /botesee/

WORKDIR /botesee
RUN uv sync --locked

COPY src/ /botesee/src

# Stage 2: Final stage
FROM python:3.12.8-slim AS final
COPY --from=base /botesee /botesee/

WORKDIR /botesee
ENV PATH "${PATH}:/botesee/.venv/bin/"
ENV PYTHONPATH "/botesee:/botesee/.venv/lib:${PYTHONPATH}"

# Discord bot
FROM final AS discord-bot
CMD ["python3", "src/discord_bot/main.py"]

# Web
FROM final AS web
COPY alembic.ini alembic.ini
COPY web.sh web.sh
COPY uvicorn_log_conf.json uvicorn_log_conf.json
RUN chmod +x web.sh
ENTRYPOINT ["./web.sh"]

# Celery
FROM final AS celery
CMD ["celery", "-A", "src.celery_app.tasks.app", "worker", "-B", "-l", "INFO", "--autoscale=20,4"]
