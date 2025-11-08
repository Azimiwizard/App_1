#!/bin/sh
set -e

# Wait for DB to be available (postgres is reachable at $DATABASE_URL host) - flask-migrate and SQLAlchemy will use DATABASE_URL
# Run DB migrations
if [ -n "$DATABASE_URL" ]; then
  echo "Running database migrations..."
  # Only run deterministic upgrades in container. Do NOT autogenerate migrations here.
  flask --app main db upgrade || { echo "Database upgrade failed; exiting."; exit 1; }
else
  echo "No DATABASE_URL set; skipping migrations (using default sqlite)."
fi

# Start the Flask app using gunicorn in production mode, fallback to flask run in development
if [ "$FLASK_ENV" = "production" ]; then
  echo "Starting app with gunicorn"
  exec gunicorn -w 4 -b 0.0.0.0:5000 main:app
else
  echo "Starting app with flask run (development)"
  flask --app main run --host=0.0.0.0 --port=5000
fi
