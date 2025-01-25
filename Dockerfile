FROM python:3.12.8-slim AS base
RUN apt-get update
RUN apt-get install build-essential curl -y
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /botesee/

WORKDIR /botesee
RUN mkdir __pypackages__ && pdm sync --prod --no-editable

ENV PATH "${PATH}:/botesee/__pypackages__/3.12/bin/"
ENV PYTHONPATH "/botesee:/botesee/__pypackages__/3.12/lib:${PYTHONPATH}"
COPY src/ /botesee/src

FROM base AS discord-bot

CMD ["python3", "src/discord_bot/main.py"]

FROM base AS web

COPY alembic.ini alembic.ini
COPY web.sh web.sh
RUN chmod +x web.sh
ENTRYPOINT ["./web.sh"]

FROM base AS celery

CMD ["celery", "-A", "src.celery.tasks.app", "worker", "-l", "INFO"]
