#!/bin/bash

# Exit on any error
echo "Starting Vercel build script..."

# Run migrations (ignore errors if DB not available during build)
echo "Running database migrations..."
python3 manage.py migrate || true

# Create superuser (ignore errors if DB not available during build)
echo "Creating superuser if needed..."
python3 manage.py create_superuser || true

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Build script completed successfully!"
