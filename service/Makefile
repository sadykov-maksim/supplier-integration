# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_BUILD = docker build
DOCKER_RUN = docker run
DOCKER_EXEC = docker exec

# Goals
.PHONY: build up down restart logs clean

# Default settings for docker-compose
DOCKER_COMPOSE_FILE := docker-compose.yml
DOCKER_COMPOSE_PROJECT_NAME := supplierIntegration

# Default goal
.DEFAULT_GOAL := help

help:
	@echo Usage: make [target]
	@echo Available targets:
	@echo - build            Build Docker images
	@echo - up               Start containers in detached mode
	@echo - down             Stop and remove containers
	@echo - restart          Restart containers
	@echo - clean            Stop and remove containers, images, and volumes
	@echo - makemigrations   Create Django migrations
	@echo - migrate          Apply Django migrations to the database
	@echo - collectstatic    Collect Django static files

build:
	@echo "Building Docker images..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) build

up:
	@echo "Starting containers in detached mode..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_COMPOSE_PROJECT_NAME) up -d

down:
	@echo "Stopping and removing containers..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_COMPOSE_PROJECT_NAME) down

restart:
	@echo "Restarting containers..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_COMPOSE_PROJECT_NAME) restart

clean:
	@echo "Cleaning up containers, images, and volumes..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_COMPOSE_PROJECT_NAME) down -v --remove-orphans
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DOCKER_COMPOSE_PROJECT_NAME) rm -f

makemigrations:
	@echo "Creating Django migrations..."
	$(DOCKER_EXEC) web python manage.py makemigrations

migrate:
	@echo "Applying Django migrations..."
	$(DOCKER_EXEC) web python manage.py migrate

collectstatic:
	@echo "Collecting Django static files..."
	$(DOCKER_EXEC) web python manage.py collectstatic --noinput --clear
