OS := $(shell uname)
VENV_NAME := my-venv
VENV_ACT := . $(VENV_NAME)/bin/activate
ifeq ($(OS), Windows_NT)
	VENV_ACT := $(VENV_NAME)/Scripts/activate
endif

build:
	@echo "Building docker image..."
	@docker build -t my-redis .


db-up:
	@echo "Starting redis server..."
	if docker ps -a | grep -q my-redis-container; then \
		echo "my-redis-container exists"; \
		docker start my-redis-container; \
	else \
		echo "my-redis-container does not exist"; \
		docker run -d -p 6379:6379 --name my-redis-container my-redis; \
	fi


add-admin: db-up
	@docker exec my-redis-container sh /usr/local/bin/init-redis.sh

down:
	@echo "Stopping Redis server"
	@docker stop my-redis-container

install-requirements:
ifeq ($(OS), Windows_NT) # Windows
	@echo "Windows OS detected"
	@python -m venv $(VENV_NAME)
	@$(VENV_ACT) && pip install -r requirements.txt
else
	@echo "Unix OS detected"
	@python3 -m venv $(VENV_NAME)
	@$(VENV_ACT) && pip install -r requirements.txt
endif

test:
	@$(VENV_ACT) && pytest

server-up: db-up
	@$(VENV_ACT) && uvicorn src.main:app --reload --env-file=.env


default-setup: build db-up add-admin install-requirements test server-up
setup: db-up install-requirements test server-up

.PHONY: build db-up down install-requirements server-up add-admin test setup default-setup
