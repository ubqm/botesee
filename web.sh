#!/bin/sh

alembic upgrade head
uvicorn bot.web.main:app --host 0.0.0.0 --port 5000
