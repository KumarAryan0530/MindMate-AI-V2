#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate --no-input

# Create superuser if needed (optional - comment out if not needed)
# python manage.py createsuperuser --no-input --email admin@example.com || true

echo "Build completed successfully!"
