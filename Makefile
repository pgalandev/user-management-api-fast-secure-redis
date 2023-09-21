OS := $(shell uname)
VENV_NAME := my-venv
VENV_ACT := . $(VENV_NAME)/bin/activate
ifeq ($(OS), Windows_NT)
	VENV_ACT := $(VENV_NAME)/Scripts/activate
endif
build:
	docker-compose build

db-up:
	docker-compose up -d

down:
	docker-compose down

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

server-up:
	@$(VENV_ACT) && uvicorn src.main:app --reload --env-file=.env


setup: build db-up install-requirements test server-up

.PHONY: build db-up down install-requirements server-up test setup
