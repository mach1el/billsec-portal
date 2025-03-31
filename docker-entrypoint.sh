#!/bin/sh

# Wait for the database
echo "Waiting for postgres..."

while ! nc -z maindb 5432; do
  sleep 1
done

echo "PostgreSQL started"

# Apply DB migrations and start server
python manage.py makemigrations billing
python manage.py migrate billing
python manage.py migrate
exec "$@"