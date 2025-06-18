#!/bin/sh
alembic upgrade head
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8000
