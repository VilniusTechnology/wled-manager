# Docker Deployment

Deploy WLED Manager using Docker and Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- A configured `.env` file based on `.env.example`

---

## 1. Configure Environment

```bash
# Copy and configure environment
cp .env.example .env

# Edit with your production values
nano .env
```

Key production settings:

```env
# Set your timezone
TIMEZONE=Europe/London

# Configure for production
DEBUG=false
LOG_LEVEL=info
NODE_ENV=production

# Set network range for your WLED devices
NETWORK_RANGE=192.168.1.0/24

# Optional: Docker registry for custom images
REGISTRY=ghcr.io
REGISTRY_USERNAME=yourusername
```

---

## 2. Build and Deploy

```bash
# Build production images
make prod-build

# Start in production mode
docker compose up -d

# View logs
docker compose logs -f
```

---

## 3. Access the Application

By default, the production setup uses `network_mode: host`, so services bind directly to the host network:

- **Web UI**: http://your-server:8080
- **API**: http://your-server:8000
- **API Docs**: http://your-server:8000/docs

---

## Persistent Storage

Defined in `docker-compose.yml` (paths configurable via `DATA_PATH` env var):

```yaml
volumes:
  - ${DATA_PATH:-./backups}:/app/backups
  - ${DATA_PATH:-./database}:/app/database
  - ${DATA_PATH:-./db}:/app/db
```

---

## Updating

```bash
# Pull latest images and restart
docker compose pull
docker compose up -d
```

---

## Backup & Recovery

### Manual Database Backup

```bash
docker compose exec backend cp /app/database/wled_devices.db /app/backups/db-backup.db
```

### Restore from Backup

1. Stop the application
2. Replace the database file with your backup
3. Restart the application

---

## Troubleshooting

### Logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Devices not found | Check `NETWORK_RANGE` matches your network |
| Connection refused | Ensure WLED devices are accessible on port 80 |
| Scheduler not running | Verify `DISABLE_*_SCHEDULER` is `false` |
