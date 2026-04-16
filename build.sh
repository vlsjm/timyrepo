#!/bin/bash
set -e

# Exit on any error
echo "Starting Vercel build script..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser if needed..."
python manage.py create_superuser

# Collect static files (if needed for production)
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build script completed successfully!"
