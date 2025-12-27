#!/bin/bash

set -e

echo "Starting the initialization process..."

python create_tables.py

echo "Starting the FastAPI server..."

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info