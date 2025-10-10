#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

# It's a good practice to wait for the DB, although depends_on with healthcheck helps.
# We'll add a small delay to be safe.
echo "Entrypoint: Waiting for database to be ready..."
sleep 5

echo "Entrypoint: Running database migrations..."
mongodb-migrate --url 'mongodb://mongodb:27017/judge?replicaSet=rs0' --migrations migrations --database judge

echo "Entrypoint: Migrations finished."

# Execute the main command (CMD) passed to the container.
# This allows the same entrypoint to be used for the API server and the worker.
echo "Entrypoint: Starting main process..."
exec "$@"