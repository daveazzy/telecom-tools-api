# TelecomTools Suite - Makefile

.PHONY: help install install-dev run docker-up docker-down test lint format clean init-db seed-db migrate

help:
	@echo "TelecomTools Suite - Available commands:"
	@echo ""
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make run            - Run the application"
	@echo "  make docker-up      - Start Docker containers"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean temporary files"
	@echo "  make init-db        - Initialize database"
	@echo "  make seed-db        - Seed database with sample data"
	@echo "  make migrate        - Run database migrations"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker-compose up -d
	@echo "Services started!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo "pgAdmin: http://localhost:5050"

docker-down:
	docker-compose down

test:
	pytest -v --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app tests
	mypy app

format:
	black app tests
	isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ dist/ build/ *.egg-info
	@echo "Cleaned temporary files"

init-db:
	python scripts/init_db.py

seed-db:
	python scripts/seed_database.py

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-rollback:
	alembic downgrade -1

migrate-history:
	alembic history --verbose

