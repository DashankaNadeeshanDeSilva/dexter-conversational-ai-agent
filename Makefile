.PHONY: setup dev test docker-build docker-run clean

# Setup environment
setup:
	pip install -r requirements.txt
	cp .env.example .env

# Run development server
dev:
	uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-down:
	docker-compose down

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/

# Create a new user token (for testing)
create-token:
	python -c "from app.utils.auth import create_token; print(create_token('testuser'))"
