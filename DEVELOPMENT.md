# Developer Guide

This guide is intended for developers who want to contribute to WLED Manager or build it from source.

## Prerequisites

- **Docker & Docker Compose**: Essential for running the containerized environment.
- **Make**: Used for running convenience commands.
- **Git**: For version control.
- **Node.js**: (Optional) If you want to run frontend tooling outside Docker.
- **Python 3.10+**: (Optional) If you want to run backend tooling outside Docker.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Vue.js UI     │────▶│  FastAPI Backend│
│   (Port 5173)   │     │   (Port 8000)   │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              ┌─────▼─────┐ ┌────▼────┐ ┌─────▼─────┐
              │  SQLite   │ │ Backups │ │   WLED    │
              │  Database │ │  Store  │ │  Devices  │
              └───────────┘ └─────────┘ └───────────┘
```

## Quick Start (Development)

The project is configured with Docker Compose for a seamless development experience with hot-reloading.

```bash
# 1. Start the development environment
make dev
```

- **Frontend**: http://localhost:5173 (Hot-reloads on change)
- **Backend API**: http://localhost:8000 (Hot-reloads on change)
- **API Docs**: http://localhost:8000/docs

## Development Workflow

### Hot Reloading
- **Backend**: Changes to files in `api/`, `scanner/`, `services/`, `models/`, and `utils/` will trigger a restart of the Uvicorn server.
- **Frontend**: Changes to `ui/src/` will trigger a browser refresh via Vite.

### Directory Structure
- `api/`: FastAPI application root.
  - `api/controllers/`: API route handlers (devices, backups, settings, etc.).
  - `api/services/`: Core business logic, schedulers, and service orchestration.
- `db/`: Database layer (connection, models, CRUD operations).
- `scanner/`: WLED discovery logic and device info retrieval.
- `models/`: Pydantic models for API requests/responses.
- `services/`: Global application settings management.
- `utils/`: Utility functions (crypto, IP resolution, config validators).
- `ui/`: Vue.js frontend application.
- `database/`: SQLite storage location (mounted volume).
- `backups/`: Device backup storage location (mounted volume).

## Commands

We use a `Makefile` to simplify common tasks:

```bash
make help           # Show all available commands

# Development
make dev            # Start dev environment
make dev-down       # Stop dev environment
make dev-logs       # Follow container logs
make dev-build      # Build development containers
make dev-rebuild    # Rebuild containers (cleans volumes/node_modules)

# Production
make prod-build     # Build production images
make prod-push      # Push images to registry
make prod-build-push # Build and push images
make prod-deploy    # Full deploy: build, push, deploy to k3s

# Kubernetes
make k3s-deploy     # Deploy to k3s cluster
make registry-login # Login to Docker registry

# Cleanup
make clean          # Clean up containers and volumes
```

## Deployment

For production deployment instructions, please refer to [DEPLOYMENT.md](DEPLOYMENT.md).

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Ensure your code is linted and formatted (`make lint`, `make format`).
4. Commit your changes (`git commit -m "Add cool feature"`).
5. Push to the branch (`git push origin feature/my-feature`).
6. Open a Pull Request.

## License

This project is licensed under the Apache License 2.0.

