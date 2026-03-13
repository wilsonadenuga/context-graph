#!/bin/bash
set -e

echo "Starting backend..."

# Initialize schema (waits for Neo4j, then applies constraints/indexes)
echo "Initializing schema..."
python /app/scripts/init_schema.py
echo "Schema initialized"

# Seed sample data
echo "Seeding sample data..."
python /app/scripts/generate_sample_data.py
echo "Sample data seeded"

# Start the application
exec "$@"
