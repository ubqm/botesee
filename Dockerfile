# Stage 1: Build stage
FROM python:3.12.8-slim AS base
RUN apt-get update
RUN apt-get install build-essential curl -y

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /botesee/

WORKDIR /botesee
RUN mkdir __pypackages__ && pdm sync --prod --no-editable

COPY src/ /botesee/src

# Stage 2: Final stage
FROM python:3.12.8-slim AS final
COPY --from=base /botesee /botesee/

WORKDIR /botesee
ENV PATH "${PATH}:/botesee/__pypackages__/3.12/bin/"
ENV PYTHONPATH "/botesee:/botesee/__pypackages__/3.12/lib:${PYTHONPATH}"

# Discord bot
FROM final AS discord-bot
CMD ["python3", "src/discord_bot/main.py"]

# Web
FROM final AS web
COPY alembic.ini alembic.ini
COPY web.sh web.sh
RUN chmod +x web.sh
ENTRYPOINT ["./web.sh"]

# Celery
FROM final AS celery
CMD ["celery", "-A", "src.celery.tasks.app", "worker", "-l", "INFO"]
