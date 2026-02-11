.DEFAULT_GOAL := help

##@ General

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: \033[36mmake <target>\033[0m\n\nAwailable targets:\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Environment

.PHONY: lock
lock: ## Lock dependencies in uv.lock.
	poetry lock

.PHONY: sync
sync: ## Install/sync dependencies from uv.lock
	poetry sync

.PHONY: clean
clean: ## Remove all temporary files and unused git references.
	git clean -fdX \
	--exclude '!.env' \
	--exclude '!.venv' \
	--exclude '!.venv/**' \
	--exclude '!.vscode' \
	--exclude '!.vscode/**'

.PHONY: lint
lint: ## Linting check
	poetry run pre-commit run --all-files

.PHONY: fix
fix: ## Fix linting errors
	poetry run ruff check . --fix

.PHONY: test
test: lint ## Run tests
	poetry run pytest -vv

.PHONY: dev
dev: ## Run dev fastapi
	poetry run fastapi run exchanger/main.py

.PHONY: makemigrations
	poetry run alembic

#-------
#.PHONY: test1
#test1: test2 ## Print test1
#	echo "test1"

#test2: test3
#	touch test2
#	echo "test2"


#-------------Alembic-------------
.PHONY: makemigrations migrate downgrade

makemigrations: ## Make migrations file
	@if [ -z "$(msg)" ]; then \
		echo ""; \
		echo "❌ Missing migration message"; \
		echo "   Usage: make migrations msg=\"your message\""; \
		echo ""; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(msg)"

migrate: ## Apply migrations to database
	poetry run alembic upgrade head

downgrade: ## Downgrade migration
	poetry run alembic downgrade -1
#---------------------------------
