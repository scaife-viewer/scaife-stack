#!/bin/sh

echo "Running migrations and populating the ATLAS database"
python manage.py prepare_db

exec "$@"
