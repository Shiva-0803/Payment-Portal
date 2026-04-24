#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting Build Process..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
echo "Collecting Static Files..."
python manage.py collectstatic --noinput

echo "Build Completed Successfully!"
