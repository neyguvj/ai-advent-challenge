#!/bin/bash
set -e

alembic upgrade head

gunicorn -b 0.0.0.0:$APP_PORT -w 4 app.main:app
