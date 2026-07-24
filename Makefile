.DEFAULT_GOAL := help

.PHONY: help all build-docker run-pipeline serve-dashboard clean clean-all clean-docker clean-python clean-logs clean-dbt clean-db clean-raw

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

all: build-docker run-pipeline serve-dashboard ## Build -> Run pipeline -> Serve dashboard 

build-docker: ## Build services
	docker compose build

run-pipeline: ## Run the data pipeline: ingestion -> staging -> core -> dbt
	docker compose run --rm pipeline

serve-dashboard: ## Serve the dashboard
	docker compose up dashboard

clean: clean-docker clean-python clean-logs clean-dbt clean-db ## Clean all (except raw data)

clean-all: clean clean-raw ## Clean ALL

clean-docker: ## Stop containers and remove volumes (reset)
	docker compose down -v

clean-python: ## Clean up python cache files
	@echo "deleting python caches..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +

clean-logs: ## Clean logs
	@echo "deleting logs..."
	@rm -rf logs/*

clean-dbt: ## Clean dbt files
	@echo "deleting dbt data..."
	@dbt clean --project-dir dbt --no-clean-project-files-only

clean-db:  ## Delete DuckDB database
	@echo "deleting duckdb database..."
	@rm -f data/*.duckdb

clean-raw: ## Delete raw data
	@echo "deleting ingested data...!"
	@rm -rf data/raw
