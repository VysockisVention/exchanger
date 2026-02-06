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

.PHONY: test
test: ## Run tests
	poetry run pytest -vv

.PHONY: dev
dev: ## Run dev fastapi
	poetry run fastapi run exchanger/main.py