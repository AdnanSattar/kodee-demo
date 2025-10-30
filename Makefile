.PHONY: up migrate setup
# Makefile for Docker-native development workflow
# Use these commands for all regular development tasks

# Start all services using Docker Compose and build if needed
up:
	docker compose up --build -d

# Stop and remove all services and persistent volumes
down:
	docker compose down

# Run Alembic database migrations inside Docker
migrate:
	docker compose exec web alembic upgrade head

# Setup = up + migrate, for convenience
setup: up migrate