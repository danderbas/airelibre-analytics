#!/bin/bash
set -e

echo "starting data ingestion..."
uv run python src/pipeline/ingest.py

echo "staging to local db..."
uv run python src/pipeline/stage.py

echo "building core tables..."
uv run python src/pipeline/build_core.py

echo "building dbt models..."
uv run dbt build