#!/bin/bash
set -e

alembic upgrade head

gunicorn -b 0.0.0.0:$APP_PORT --capture-output --log-level debug -w 1 app.main:app
