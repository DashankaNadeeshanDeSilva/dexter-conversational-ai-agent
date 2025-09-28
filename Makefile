# Makefile for Dexter Conversational AI Agent to automate the development workflow
#
# Usage:
#   make help                 # Show common targets
#   make setup                # Setup environment
#   make dev                  # Run development server
#   make test                 # Run tests
#   make docker-build         # Build Docker image (compose)
#   make docker-run           # Run Docker container (compose)
#   make docker-down          # Stop Docker containers (compose)
#   make lambda-build         # Build Lambda container image (amd64)
#   make lambda-run           # Run Lambda container locally (use ENV_FILE=.env.lambda)
#   make lambda-invoke-health # Invoke /health against local Lambda
#   make lambda-printenv      # Debug: print env inside Lambda container
#   make lambda-pinecone-check# Debug: verify Pinecone access inside container
.PHONY: setup dev test docker-build docker-run docker-down clean install-lambda lambda-build lambda-run lambda-invoke-health test-lambda lambda-printenv lambda-pinecone-check

# Setup environment
setup:
	pip install -r requirements.txt

# Default env file for Lambda runs; override with ENV_FILE=.env.lambda
ENV_FILE ?= .env

# Run development server
dev:
	uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/

# Docker commands (simplified: app + mongodb only)
docker-build:
	docker-compose build --no-cache

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
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/

# Create a new user token (for testing)
create-token:
	python -c "from app.utils.auth import create_token; print(create_token('testuser'))"

# Lambda testing
test-lambda:
	pytest -q tests/test_lambda_handler.py

# Install Lambda dependencies
install-lambda:
	pip install mangum

# Allow selecting which env file to pass to the Lambda container.
# Usage:
#   make lambda-run                     # uses .env (default)
#   make lambda-run ENV_FILE=.env.lambda
ENV_FILE ?= .env

# Build Lambda container image
lambda-build:
	# Build for linux/amd64 and LOAD into local docker (required to run locally)
	docker buildx build --platform linux/amd64 -f Dockerfile.lambda -t dexter-lambda:latest . --load

# Run Lambda container locally with Runtime Interface Emulator
# Note: for real Lambda simulation, mount AWS RIE or use `sam local`.
# Use .env.lambda for Lambda container
lambda-run:
	# Pass environment via selected env file to avoid empty values causing Pydantic validation errors
	docker run --rm --platform linux/amd64 -p 9000:8080 --env-file $(ENV_FILE) dexter-lambda:latest

# Invoke the locally running Lambda container
lambda-invoke-health:
	curl -s "http://localhost:9000/2015-03-31/functions/function/invocations" \
	  -d '{"version":"2.0","routeKey":"GET /health","rawPath":"/health","rawQueryString":"","headers":{"content-type":"application/json","host":"localhost","x-forwarded-proto":"http"},"requestContext":{"http":{"method":"GET","path":"/health","sourceIp":"127.0.0.1","userAgent":"curl/8.5.0","protocol":"HTTP/1.1"}},"body":null,"isBase64Encoded":false}' | jq '.'


