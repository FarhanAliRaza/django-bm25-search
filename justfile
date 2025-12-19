# django-pg-textsearch justfile

# Default recipe - show available commands
default:
    @just --list

# Install the package in development mode
install:
    uv sync --all-extras --all-groups

# Run all tests
test:
    uv run pytest

# Run unit tests only (no database required)
test-unit:
    uv run pytest tests/unit -v

# Run integration tests only (requires PostgreSQL)
test-integration:
    uv run pytest tests/integration -v

# Run tests with coverage
test-cov:
    uv run pytest --cov=src/django_pg_textsearch --cov-report=html --cov-report=term

# Run a specific test file
test-file file:
    uv run pytest {{file}} -v

# Format code with black
fmt:
    uv run ruff format src tests

# Check formatting without modifying
fmt-check:
    uv run ruff format --check src tests

# Lint with ruff
lint:
    uv run ruff check src tests

# Lint and fix issues
lint-fix:
    uv run ruff check --fix src tests

# Run all checks (format + lint)
check: fmt-check lint

# Clean build artifacts
clean:
    rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete

# Build the package
build: clean
    uv build

# Docker commands (for pg_textsearch)

# Build PostgreSQL image with pg_textsearch
docker-build:
    docker build -t postgres-pg-textsearch:17 -f .docker/Dockerfile.postgres .

# Start PostgreSQL with pg_textsearch
docker-up:
    docker compose up -d
    @echo "Waiting for PostgreSQL to be ready..."
    @sleep 5
    docker compose exec postgres psql -U postgres -d django_pg_textsearch_test -c "CREATE EXTENSION IF NOT EXISTS pg_textsearch;"

# Stop PostgreSQL
docker-down:
    docker compose down

# View PostgreSQL logs
docker-logs:
    docker compose logs -f postgres

# Run Django migrations for test models
migrate:
    uv run python -c "import django; django.setup(); from django.core.management import call_command; call_command('migrate', '--run-syncdb')"

# CI simulation

# Run full CI locally
ci: check test-unit

# Run full CI with integration tests (requires PostgreSQL)
ci-full: check test

# Development helpers

# Watch tests and re-run on changes (requires pytest-watch)
test-watch:
    uv run ptw tests/unit

# Open coverage report in browser
cov-open:
    open htmlcov/index.html || xdg-open htmlcov/index.html

# Type check with mypy (if installed)
typecheck:
    uv run mypy src/django_pg_textsearch --ignore-missing-imports

# Show package version
version:
    @uv run python -c "from django_pg_textsearch import __version__; print(__version__)"

# Add a dependency
add *args:
    uv add {{args}}

# Add a dev dependency
add-dev *args:
    uv add --dev {{args}}

# Update all dependencies
update:
    uv sync --upgrade

# Lock dependencies
lock:
    uv lock
