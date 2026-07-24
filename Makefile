CONFIG = config.yaml

.PHONY: install ingest stage build-core dbt-run all

.DEFAULT_GOAL := all

init-logs:
	@mkdir -p logs

install:
	pip install .

ingest: init-logs
	python src/pipeline/ingest.py | tee -a logs/ingest_$(shell date +%Y%m%d).log

stage: init-logs
	python src/pipeline/stage.py | tee -a logs/stage_$(shell date +%Y%m%d).log

build-core: init-logs
	python src/pipeline/build_core.py | tee -a logs/core_$(shell date +%Y%m%d).log

dbt-run:
	@cd dbt && dbt seed && dbt run
	
all: install ingest stage build-core dbt-run

clean-python:
	@echo "deleting python caches..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +

clean-logs:
	@echo "deleting logs..."
	@rm -rf logs/*

clean-dbt:
	@echo "deleting dbt data..."
	@cd dbt && dbt clean

clean-db:
	@echo "deleting duckdb database..."
	@rm data/*.duckdb

clean-raw:
	@echo "deleting ingested data!"
	@rm -rf data/raw

clean: clean-python clean-logs clean-dbt clean-db
	@echo "clean complete (make clean-raw|clean-all to erase raw data)"

clean-all: clean clean-raw