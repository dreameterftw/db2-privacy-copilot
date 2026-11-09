.PHONY: help setup db-up db-down db-logs bootstrap seed test clean lint format

help:
	@echo "Db2 Privacy Copilot - Available Commands"
	@echo "========================================"
	@echo "  make setup      - Initial project setup"
	@echo "  make db-up      - Start Db2 container"
	@echo "  make db-down    - Stop Db2 container"
	@echo "  make db-logs    - Watch Db2 logs"
	@echo "  make bootstrap  - Initialize database schema"
	@echo "  make seed       - Generate synthetic data"
	@echo "  make test       - Run test suite"
	@echo "  make lint       - Run linters (ruff, mypy)"
	@echo "  make format     - Format code with ruff"
	@echo "  make security   - Run security scans"
	@echo "  make clean      - Clean up generated files"
	@echo "  make reset-db   - Complete database reset"

setup:
	@echo "Running setup..."
	@bash setup.sh || cmd /c setup.bat

db-up:
	docker compose up -d
	@echo "Db2 starting... This takes 5-10 minutes on first run."
	@echo "Run 'make db-logs' to watch progress."

db-down:
	docker compose down

db-logs:
	docker compose logs -f db2

bootstrap:
	python app/bootstrap.py

seed:
	python eval/seed.py

test:
	pytest -v --cov=app --cov-report=term-missing

test-fast:
	pytest -v -x

lint:
	ruff check app/ eval/ tests/
	mypy app/

format:
	ruff format app/ eval/ tests/

security:
	bandit -r app/
	pip-audit

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache 2>/dev/null || true

reset-db:
	@echo "⚠️  WARNING: This will delete all Db2 data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down; \
		rm -rf db2data/; \
		echo "Database reset complete. Run 'make db-up' to start fresh."; \
	fi

# Development workflow shortcuts
dev-setup: setup db-up
	@echo "Waiting for Db2 to initialize..."
	@echo "This may take 5-10 minutes. Please be patient."
	@sleep 300
	$(MAKE) bootstrap seed test

quick-test: format lint test-fast

all: lint test security
