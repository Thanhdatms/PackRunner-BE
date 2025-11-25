#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Running migrations..."
python manage.py migrate

echo "Starting server..."
exec "$@"
