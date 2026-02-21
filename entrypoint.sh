#!/bin/sh
set -e

echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done


echo "Running database migrations..."
alembic -c alembic/alembic.ini upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000