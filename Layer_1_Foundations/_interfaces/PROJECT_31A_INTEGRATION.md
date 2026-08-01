# PROJECT VENUS — PROJECT 31A INTEGRATION LAYER

**Version**: 1.0  
**Purpose**: Interface definitions for consumer projects (e.g., Project 31A).

---

## 1. Design Principles

1. **No fork, no copy** — Venus is upstream; 31A consumes via interface
2. **Interface-based contract** — Stable, versioned API surface
3. **Pull, not push** — Consumer fetches what it needs
4. **Constitution-governed** — All consumption must satisfy UVCOS

---

## 2. Integration Model

```
┌─────────────────────────┐
│        Venus             │
│  Ontology  Schemas  DSL │
│  Graph   Compiler  Rules │
│  Memory   Runtime  Evol  │
└──────────┬──────────────┘
           │ Interfaces
           ▼
┌─────────────────────────┐
│   Integration Layer      │
│  ┌────────────────────┐  │
│  │  API Gateway        │  │
│  │  Query Service      │  │
│  │  Schema Registry    │  │
│  │  Graph Export       │  │
│  │  Asset Bundler      │  │
│  │  Auth & Audit       │  │
│  └────────────────────┘  │
└──────────┬──────────────┘
           │ API Calls
           ▼
┌─────────────────────────┐
│     Project 31A          │
│  Build   Deploy   Operate│
│  Plan    Monitor  Improve│
└─────────────────────────┘
```

---

## 3. Interface Definitions

### 3.1 Schema Registry API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/schemas/list` | GET | List all available schemas |
| `/schemas/:id` | GET | Get schema by ID |
| `/schemas/:id/version/:v` | GET | Get specific schema version |
| `/schemas/search?q=` | GET | Search schemas |

### 3.2 Ontology Query API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ontology/types` | GET | List all ontology types |
| `/ontology/types/:id` | GET | Type details with inheritance chain |
| `/ontology/entities` | GET | List entities by type |
| `/ontology/entities/:id` | GET | Entity full definition |
| `/ontology/search?q=` | GET | Search ontology |

### 3.3 Knowledge Graph API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/nodes` | GET | List all nodes |
| `/graph/edges` | GET | List all edges |
| `/graph/edges/:type` | GET | Edges filtered by type |
| `/graph/subgraph/:node_id` | GET | 1-hop neighborhood |
| `/graph/export/:format` | GET | Export graph (json/cypher) |

### 3.4 Artifact Export API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/artifacts/list` | GET | List generated artifacts |
| `/artifacts/:id` | GET | Get artifact content |
| `/artifacts/:id/format/:fmt` | GET | Export in requested format |
| `/bundles/create` | POST | Create custom artifact bundle |

### 3.5 Constitution API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/constitution` | GET | Current constitution text |
| `/constitution/rules` | GET | All rules |
| `/constitution/validate` | POST | Validate artifact against constitution |

### 3.6 Memory Query API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/memory/query` | POST | Semantic search over memory |
| `/memory/decisions` | GET | Decision history |
| `/memory/research` | GET | Research findings |

---

## 4. Authentication & Authorization

- API key authentication for all endpoints
- Rate limiting: 1000 req/min per key
- Audit logging: all requests logged with timestamp, key, endpoint
- Access tiers:
  - `read:basic` — public schemas, ontology, graph
  - `read:full` — all read endpoints
  - `write:export` — artifact bundling
  - `admin` — full access

---

## 5. Versioning & Compatibility

- API versioned via URL path (`/v1/schemas/list`)
- Schema versioning via semantic versioning
- Backward compatibility guaranteed within major version
- Deprecation: 6-month notice before breaking change
