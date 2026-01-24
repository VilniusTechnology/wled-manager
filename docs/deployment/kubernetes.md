# Kubernetes Deployment

Deploy WLED Manager to a Kubernetes cluster.

## Prerequisites

- kubectl and access to a Kubernetes cluster
- The `k8s/` directory contains all necessary manifests

---

## 1. Configure Secrets

Edit `k8s/backend-secret.yaml` and set your secret key:

```bash
# Generate a random secret
openssl rand -base64 32

# Edit the secret file
nano k8s/backend-secret.yaml
```

---

## 2. Configure Settings

Edit `k8s/backend-configmap.yaml` to match your environment:

- `TIMEZONE`: Your timezone (e.g., `Europe/London`)
- `NETWORK_RANGE`: Your local network CIDR (e.g., `192.168.1.0/24`)
- Scheduler settings as needed

---

## 3. Deploy

```bash
# Apply all manifests
kubectl apply -k k8s/

# Check deployment status
kubectl -n wled get pods

# View logs
kubectl -n wled logs -f deployment/wled-manager-backend
```

---

## 4. Ingress Configuration

The included `ingress-route.yaml` is configured for Traefik. Modify for your ingress controller:

```yaml
# Example: Update host to your domain
- match: Host(`wled.yourdomain.com`)
```

---

## Persistent Storage

Configure appropriate PersistentVolumeClaims for your cluster storage class. The `DATA_PATH` environment variable in `.env` sets the host path for persistence.

---

## Updating

```bash
# Update images and rollout
kubectl -n wled rollout restart deployment/wled-manager-backend
kubectl -n wled rollout restart deployment/wled-manager-frontend
```

---

## Backup & Recovery

### Manual Database Backup

```bash
kubectl -n wled exec deployment/wled-manager-backend -- cp /app/database/wled_devices.db /app/backups/db-backup.db
```

### Restore from Backup

1. Stop the application
2. Replace the database file with your backup
3. Restart the application

---

## Troubleshooting

### Logs

```bash
kubectl -n wled logs -f deployment/wled-manager-backend
kubectl -n wled logs -f deployment/wled-manager-frontend
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Devices not found | Check `NETWORK_RANGE` matches your network |
| Connection refused | Ensure WLED devices are accessible on port 80 |
| Scheduler not running | Verify `DISABLE_*_SCHEDULER` is `false` |
