#!/bin/bash
set -e

# echo "[Fetching ATLAS data]"
# sh ./scripts/fetch-explorehomer-data.sh

# echo "[Stage data]"
# python manage.py stage_atlas_data --rebuild

# TODO: Fetch / stage Pedalion data
echo "[Running migrations and populating the ATLAS database]"
python manage.py prepare_db --force
