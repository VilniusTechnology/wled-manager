# WLED Manager - Production Deployment Guide

This guide covers deploying WLED Manager to production environments.

## Deployment Methods

- **[Docker Deployment](docker.md)** - Using Docker Compose for standalone deployments
- **[Kubernetes Deployment](kubernetes.md)** - For orchestrated container environments

## Prerequisites

- A configured `.env` file based on `.env.example`
- Access to your target deployment environment

## Persistent Storage

Both deployment methods use persistent volumes for:

- **Database**: SQLite database at `/app/database/`
- **Backups**: Device configuration backups at `/app/backups/`

## Health Checks

The API exposes health endpoints:

- `GET /health` - Basic health check
- `GET /api/schedulers/status` - Scheduler status

## Security Considerations

- Keep `.env` file secure and never commit it
- Use HTTPS in production with a reverse proxy
- Restrict network access to the management interface
- Regularly update to the latest version
