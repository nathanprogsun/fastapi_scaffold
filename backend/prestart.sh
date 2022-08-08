#! /usr/bin/env bash

# Let the DB start
python src/backend_pre_start.py

# Run migrations for MySQL
alembic upgrade head

# Create initial data in DB
python app/initial_data.py

# Clean legacy tasks
python app/clean_tasks.py
