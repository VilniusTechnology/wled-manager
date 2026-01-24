ifneq (,$(wildcard .env))
  include .env
  export
  ifndef NETRC
    NETRC := $(shell mktemp)
  endif
endif

# WLED Manager Makefile
# export KUBECONFIG := $(HOME)/.kube/config

.PHONY: help dev dev-down dev-logs dev-build clean test lint format docker-build docker-push docker-up docker-down docker-logs k3s-deploy prod-build-push prod-deploy registry-login

# Per-image versions (for cases where UI and API releases differ).
# By default these attempt to be derived from repository version files.
# You can override explicitly: make API_VERSION=1.2.3 UI_VERSION=2.0.0 prod-build
REGISTRY_HOST := $(shell echo "$(REGISTRY)" | sed -E -e 's,^https?://([^/]+)/?.*$$,\1,')

API_REPO ?= wled-manager-backend
API_IMAGE ?= $(REGISTRY_HOST)/$(API_REPO)

UI_REPO ?= wled-manager-frontend
UI_IMAGE ?= $(REGISTRY_HOST)/$(UI_REPO)

define GET_VERSION_CMD
	repo_name=$$1; \
	if [ -z "$(REGISTRY_HOST)" ]; then echo "Error: REGISTRY is not set correctly" >&2; exit 1; fi; \
	tags_url="http://$(REGISTRY_HOST)/v2/$$repo_name/tags/list"; \
	echo "Fetching tags for $$repo_name from $$tags_url" >&2; \
	tags=$$(curl -k --netrc-file $(NETRC) -fsL "$$tags_url" | sed -n 's/.*"tags":\[\(.*\)\].*/\1/p' | tr ',' '\n' | sed -E 's/[^0-9.]*([0-9]+\.[0-9]+\.[0-9]+).*/\1/' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$$' | sort -V | tail -n1); \
	if [ -z "$$tags" ]; then echo "Error: Failed to determine latest version for $$repo_name from registry." >&2; exit 1; fi; \
	echo $$tags;
endef

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Development with hot reloading (uses 'dev' tag)
dev-build: ## Build development containers with 'dev' tag
	API_VERSION=dev UI_VERSION=dev VERSION=dev docker compose -f docker-compose.dev.yml build

dev-rebuild: ## Rebuild development containers (cleans volumes/node_modules)
	docker compose -f docker-compose.dev.yml down -v
	API_VERSION=dev UI_VERSION=dev VERSION=dev docker compose -f docker-compose.dev.yml build --no-cache
	docker compose -f docker-compose.dev.yml up -d

dev: ## Start development containers with hot reloading
	docker compose -f docker-compose.dev.yml up -d

dev-down: ## Stop development containers
	docker compose -f docker-compose.dev.yml down

dev-logs: ## View development container logs
	docker compose -f docker-compose.dev.yml logs -f



# Production Docker commands (uses VERSION variable)
prod-build: registry-login ## Build production containers with specified VERSION/API_VERSION/UI_VERSION (default: latest) for linux/amd64
	@get_version() { \
		$(GET_VERSION_CMD) \
	}; \
	API_VERSION=$${API_VERSION:-$$(get_version "$(API_REPO)")}; \
	UI_VERSION=$${UI_VERSION:-$$(get_version "$(UI_REPO)")}; \
	echo "Building API version: $$API_VERSION  UI version: $$UI_VERSION for linux/amd64"; \
	docker buildx build --platform linux/amd64 --build-arg VERSION=$$API_VERSION -t $(API_IMAGE):$$API_VERSION --load -f Dockerfile.backend .; \
	docker buildx build --platform linux/amd64 --build-arg VERSION=$$UI_VERSION -t $(UI_IMAGE):$$UI_VERSION --load -f Dockerfile.frontend .

prod-push: registry-login ## Push images to registry with specified API_VERSION and UI_VERSION
	@get_version() { \
		$(GET_VERSION_CMD) \
	}; \
	API_VERSION=$${API_VERSION:-$$(get_version "$(API_REPO)")}; \
	UI_VERSION=$${UI_VERSION:-$$(get_version "$(UI_REPO)")}; \
	echo "Pushing API version: $$API_VERSION  UI version: $$UI_VERSION"; \
	docker push $(API_IMAGE):$$API_VERSION; \
	docker push $(UI_IMAGE):$$UI_VERSION

registry-login: ## Login to the configured registry (prompts for password)
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Error: REGISTRY is not set in .env file."; exit 1; \
	fi; \
	if [ -z "$$REGISTRY_USERNAME" ]; then \
		echo "Error: REGISTRY_USERNAME is not set in .env file."; exit 1; \
	fi; \
	if [ -z "$$REGISTRY_PASSWORD" ]; then \
		if [ -f "$(NETRC)" ]; then \
			REGISTRY_PASSWORD=$$(awk '$$6 != "" {print $$6}' "$(NETRC)" | head -n1); \
		fi; \
		if [ -z "$$REGISTRY_PASSWORD" ]; then \
			read -s -p 'Registry password: ' REGISTRY_PASSWORD; \
			echo; \
		else \
			echo "Using cached REGISTRY_PASSWORD from .netrc"; \
		fi; \
	else \
		echo "Using provided REGISTRY_PASSWORD"; \
	fi; \
	export REGISTRY_PASSWORD; \
	echo "$$REGISTRY_PASSWORD" | docker login $(REGISTRY_HOST) --username $$REGISTRY_USERNAME --password-stdin; \
	echo "machine $(REGISTRY_HOST) login $$REGISTRY_USERNAME password $$REGISTRY_PASSWORD" > $(NETRC); \
	chmod 600 $(NETRC); \
	echo "Registry login successful and .netrc file updated."

# K3s Deployment
k3s-deploy: registry-login ## Deploy to k3s cluster with specified API_VERSION/UI_VERSION (default: latest)
	@get_version() { \
		$(GET_VERSION_CMD) \
	}; \
	API_VERSION=$${API_VERSION:-$$(get_version "$(API_REPO)")}; \
	UI_VERSION=$${UI_VERSION:-$$(get_version "$(UI_REPO)")}; \
	echo "Deploying API version: $$API_VERSION  UI version: $$UI_VERSION to k3s"; \
	sed -i.bak "s|image: .*wled-manager-backend:.*|image: $(API_IMAGE):$$API_VERSION|" .k8s/backend-deployment.yaml && rm .k8s/backend-deployment.yaml.bak; \
	sed -i.bak "s|image: .*wled-manager-frontend:.*|image: $(UI_IMAGE):$$UI_VERSION|" .k8s/frontend-deployment.yaml && rm .k8s/frontend-deployment.yaml.bak; \
	kubectl apply -k .k8s/; \
	echo "Deployment complete. Checking rollout status..."; \
	kubectl rollout status deployment/wled-manager-backend -n wled; \
	kubectl rollout status deployment/wled-manager-frontend -n wled

prod-build-push: prod-build prod-push ## Build production images and push them to the configured registry (no deployment)

prod-deploy: registry-login ## Auto-generate version from datetime and deploy (Build -> Push -> K3s)
	if [ -z "$$REGISTRY_PASSWORD" ] && [ -f "$(NETRC)" ]; then \
		REGISTRY_PASSWORD=$$(awk '$$6 != "" {print $$6}' "$(NETRC)" | head -n1); \
	fi; \
	if [ -z "$$REGISTRY_PASSWORD" ]; then echo "Error: Failed to retrieve password for deployment." >&2; exit 1; fi; \
	NEW_VERSION=$$(date +%Y.%m.%d.%H%M%S); \
	echo "Generated new version: $$NEW_VERSION"; \
	echo "Pruning build cache to prevent stale code..."; \
	docker builder prune -fa; \
	$(MAKE) prod-build prod-push k3s-deploy API_VERSION=$$NEW_VERSION UI_VERSION=$$NEW_VERSION REGISTRY_PASSWORD="$$REGISTRY_PASSWORD"

# Cleanup
clean: ## Clean up containers and volumes
	docker compose down -v --remove-orphans
	docker compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
