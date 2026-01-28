#!/usr/bin/env bash
# Build script for Render

set -o errexit

pip install -r requirements.txt

# Initialize database
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all(); print('Database initialized!')"
