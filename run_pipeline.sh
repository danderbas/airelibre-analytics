#!/bin/bash
set -e


echo "starting data ingestion..."
uv run python src/pipeline/ingest.py

echo "dumping raw data into the database..."
uv run python src/pipeline/raw_dump.py

echo "staging..."
uv run python src/pipeline/stage.py

echo "building core tables..."
uv run python src/pipeline/core_build.py

echo "building dbt models..."
uv run dbt build