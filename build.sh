#!/usr/bin/env bash
set -o errexit

python manage.py collectstatic --no-input
python manage.py migrate

# Ensure media directories exist
mkdir -p media/products
mkdir -p media/banners