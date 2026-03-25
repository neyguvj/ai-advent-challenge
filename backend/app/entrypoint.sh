#!/bin/bash
set -e

alembic upgrade head

gunicorn -b 0.0.0.0:$APP_PORT --capture-output -w 4 app.main:app
