#!/bin/bash
APP_PORT=${PORT:-8000}
echo "Using port ${APP_PORT}"
cd /app/

/opt/venv/bin/python manage.py migrate
/opt/venv/bin/gunicorn cfehome.wsgi:application --bind "0.0.0.0:$APP_PORT"