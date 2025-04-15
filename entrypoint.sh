#!/bin/bash
set -e

# Defaults (can be overridden via environment variables)
APP_MODULE=${APP_MODULE:-main:app}
WORKERS=${WORKERS:-3}
BIND=${BIND:-0.0.0.0:8000}
TIMEOUT=${TIMEOUT:-60}
LOG_LEVEL=${LOG_LEVEL:-info}
ACCESS_LOG=${ACCESS_LOG:--}
ERROR_LOG=${ERROR_LOG:--}

cd /app

echo "Starting Gunicorn with:"
echo "  app: $APP_MODULE"
echo "  workers: $WORKERS"
echo "  bind: $BIND"
echo "  timeout: $TIMEOUT"
echo "  loglevel: $LOG_LEVEL"

exec gunicorn "$APP_MODULE" \
    --workers "$WORKERS" \
    -k uvicorn.workers.UvicornWorker \
    --bind "$BIND" \
    --timeout "$TIMEOUT" \
    --log-level "$LOG_LEVEL" \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG"
