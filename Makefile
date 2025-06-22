# Variables
DOCKER_COMPOSE=docker-compose
SERVICE_NAME=fever-postgres
DB_USER=fever_user
DB_NAME=fever_db
POETRY=poetry
HOST=localhost
PORT=8000

# Default target
.DEFAULT_GOAL := help

# Run the Uvicorn server
run:
	$(POETRY) run uvicorn fever_integration.main:app --host $(HOST) --port $(PORT) --reload

build-docker:
	docker build -t fever-app . \

run-docker:
	docker run --name fever_app \
		--network fever-net \
		-p 8000:8000 \
		-e DB_URL="postgresql+psycopg2://$(DB_USER):secret@$(SERVICE_NAME):5432/$(DB_NAME)" \
		-d fever-app

# Start PostgreSQL with Docker
start-db:
	docker network inspect fever-net >/dev/null 2>&1 || docker network create fever-net
	docker run --name $(SERVICE_NAME) \
	--network fever-net \
	-e POSTGRES_USER=$(DB_USER) \
	-e POSTGRES_PASSWORD=secret \
	-e POSTGRES_DB=$(DB_NAME) \
	-p 5432:5432 \
	-d postgres

# Stop and remove the PostgreSQL container
stop-db:
	docker stop $(SERVICE_NAME) && docker rm $(SERVICE_NAME)

# Open a psql shell inside the postgres container
psql:
	docker exec -it $(SERVICE_NAME) psql -U $(DB_USER) -d $(DB_NAME)

# Install dependencies using Poetry
install:
	$(POETRY) build
	$(POETRY) install

# Run tests with coverage
test:
	$(POETRY) run pytest --cov=fever_integration tests/

# Help message
help:
	@echo "Usage:"
	@echo "  make run        - Run Uvicorn server"
	@echo "  make start-db   - Start PostgreSQL in Docker"
	@echo "  make stop-db    - Stop and remove PostgreSQL container"
	@echo "  make psql       - Open psql in Docker"
	@echo "  make install    - Install Python dependencies"
	@echo "  make test       - Run tests with coverage"

