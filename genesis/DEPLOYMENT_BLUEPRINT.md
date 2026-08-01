# GENESIS-I DEPLOYMENT BLUEPRINT

**Version**: 1.0.0

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                    Client Layer                   │
│  CLI  │  Studio Web UI  │  API Clients  │  CI/CD │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                 API Gateway                      │
│  Auth │  Rate Limit │  Audit │  Route to Service │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              Genesis-I Services                   │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Compiler  │ │ Runtime  │ │ Knowledge Graph  │ │
│  │ Service   │ │ Service  │ │ Service          │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Validator │ │ Indexer  │ │ Memory Service   │ │
│  │ Service   │ │ Service  │ │                  │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                 Storage Layer                     │
│                                                   │
│  PostgreSQL  │  Neo4j  │  Redis  │  S3/MinIO     │
│  (metadata)  │ (graph) │ (cache) │ (artifacts)   │
└─────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: Single Server (Development)

```bash
python3 -m genesis # Run CLI directly
```

### Option 2: Docker Compose (Production)

```yaml
version: "3.9"
services:
  compiler:
    image: venus/genesis-compiler:latest
    volumes:
      - ./repository:/venus
    environment:
      - GENESIS_DEBUG=false
  graph:
    image: neo4j:5
    environment:
      - NEO4J_AUTH=neo4j/password
  api:
    image: venus/genesis-api:latest
    ports:
      - "8080:8080"
    depends_on:
      - compiler
      - graph
```

### Option 3: Kubernetes (Scalable)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: genesis-compiler
spec:
  replicas: 3
  selector:
    matchLabels:
      app: genesis-compiler
  template:
    spec:
      containers:
      - name: compiler
        image: venus/genesis-compiler:latest
        env:
        - name: GENESIS_WORKSPACE
          value: "/data"
        volumeMounts:
        - name: repo
          mountPath: "/data"
      volumes:
      - name: repo
        persistentVolumeClaim:
          claimName: venus-repo-pvc
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GENESIS_DEBUG` | `false` | Enable debug logging |
| `GENESIS_API_HOST` | `localhost` | API binding address |
| `GENESIS_API_PORT` | `8080` | API port |
| `GENESIS_WORKSPACE` | `.` | Workspace root |
| `GENESIS_LOG_LEVEL` | `INFO` | Log level |

## Monitoring

```python
from genesis.diagnostics import Diagnostics
diag = Diagnostics()
health = diag.run("quick")
# Integrate with Prometheus / CloudWatch
```

## Disaster Recovery

1. **Graph backup**: Export Cypher from KnowledgeGraphEngine
2. **Metadata backup**: Save MetadataEngine state
3. **Artifact backup**: Generated artifacts in `/build`
4. **Recovery**: Re-index from source + re-compile
