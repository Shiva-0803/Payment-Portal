#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting Build Process..."

# Install dependencies
pip install -r requirements.txt

# Run migrations to ensure database tables exist (e.g., django_session)
echo "Running Database Migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting Static Files..."
python manage.py collectstatic --noinput

echo "Syncing internal users..."
python sync_credentials.py

echo "Build Completed Successfully!"
