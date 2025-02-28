#!/bin/sh

alembic upgrade head
uvicorn src.web.main:app --host 0.0.0.0 --port 5000 --log-config uvicorn_log_conf.json
