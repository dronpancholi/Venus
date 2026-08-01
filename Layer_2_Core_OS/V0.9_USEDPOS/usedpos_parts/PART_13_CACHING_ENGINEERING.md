# PART 13 — Caching Engineering
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Caching Engineering defines when, where, and how to cache data across the VENUS stack. Caching is one of the highest-leverage performance tools available, but also one of the most dangerous if implemented without discipline. Phil Karlton's famous observation — "There are only two hard things in Computer Science: cache invalidation and naming things" — remains as true today as ever.

---

## 2. When to Cache

Cache when ALL of the following are true:
1. The data is expensive to compute or fetch (database round-trip, external API call)
2. The data is read significantly more frequently than it changes
3. Staleness is tolerable or invalidation is feasible
4. The cached volume is manageable (doesn't exhaust memory)

Do NOT cache when:
- Data changes on every request
- Real-time accuracy is a business requirement
- Data is user-specific with no TTL strategy
- Cache invalidation would be more complex than the benefit gained

---

## 3. Caching Layers

### 3.1 Client-Side Cache (Browser)
```
Cache-Control: max-age=3600, stale-while-revalidate=86400
ETag: "abc123"
Last-Modified: Wed, 01 Jan 2025 00:00:00 GMT

Use for:
  - Static assets (images, CSS, JS): max-age=31536000, immutable
  - API responses: stale-while-revalidate where tolerable
  - Never cache authenticated data without private directive
```

### 3.2 CDN / Edge Cache
- Static assets: infinite TTL with content-hash-based cache busting
- API responses: CDN cache for public, non-personalized data
- Vary header for content negotiation
- Purge API integration for cache invalidation on content update
- WAF at CDN layer for DDoS protection

### 3.3 Application-Level Cache (In-Process)
- Short-lived, small-volume, frequently accessed data
- Feature flags, configuration, static lookup tables
- LRU eviction strategy
- TTL: 30–300 seconds
- No distributed coordination required

### 3.4 Distributed Cache (Redis — Primary)
- Session storage
- Rate limiting counters
- Distributed locks
- Shared computation results
- User preference data
- Shopping cart / temporary state

### 3.5 Database Query Cache
- PostgreSQL's shared_buffers caches frequently accessed pages
- Do not rely on application-level query caching (deprecated in MySQL 8.0)
- Use read replicas for analytics / reporting queries

---

## 4. Cache Patterns

### 4.1 Cache-Aside (Lazy Loading) — Default Pattern
```
1. Application checks cache
2. MISS: Fetch from database, store in cache, return
3. HIT: Return cached value

Pros: Only caches what's needed; tolerates cache failures
Cons: Cache miss penalty; potential stampede
```

### 4.2 Write-Through
```
1. Application writes to cache and database simultaneously
2. All reads guaranteed fresh from cache

Pros: Cache always warm; no read latency on cache miss
Cons: Write latency increased; may cache infrequently read data
```

### 4.3 Write-Behind (Write-Back)
```
1. Application writes to cache only
2. Cache asynchronously flushes to database

Pros: Lowest write latency
Cons: Data loss risk if cache fails before flush; complexity
Use only for non-critical, high-write metrics data
```

### 4.4 Read-Through
```
1. Application only reads from cache
2. Cache is responsible for fetching from DB on miss

Implementation: Redis + Lua script or cache library with DB callback
```

---

## 5. Cache Invalidation Strategies

| Strategy | When to Use |
|---|---|
| **TTL expiry** | Data with known staleness tolerance |
| **Event-driven invalidation** | Cache invalidated on domain event (OrderUpdated → invalidate order cache) |
| **Tag-based invalidation** | Invalidate all items with a tag (all orders for user X) |
| **Write-through** | Data that must always be fresh in cache |
| **Cache versioning** | Increment cache key version on model change |

### 5.1 Cache Key Design
```
Pattern: {service}:{entity}:{id}:{version}

Examples:
  orders:order:ORD-001:v1
  users:profile:USR-123:v2
  products:catalog:page:2:v1
  rate-limits:ip:192.168.1.1
```

---

## 6. Redis Configuration Standards

```yaml
maxmemory: 2gb
maxmemory-policy: allkeys-lru  # Evict least-recently-used when full
timeout: 0                     # Keep connections alive
tcp-keepalive: 300
save: ""                       # Disable RDB for pure cache nodes
appendonly: yes                # Enable AOF for session/lock data
requirepass: <strong-password>
tls-port: 6380
```

### 6.1 Redis HA Architecture
```
Redis Cluster: 3 primary + 3 replica nodes
Sentinel: For standalone setups < 100GB
Read replicas: Separate from write primary
```

---

## 7. Cache Stampede Prevention

### 7.1 Probabilistic Early Expiration
Randomly expire cache slightly before TTL for high-traffic keys to allow one process to warm the cache before expiry.

### 7.2 Mutex Lock on Cache Miss
```
1. Thread 1 misses cache → acquires distributed lock → fetches → populates cache → releases lock
2. Thread 2 misses cache → lock exists → waits → reads from cache once Thread 1 completes
```

### 7.3 Stale-While-Revalidate
Serve stale cache while asynchronously refreshing in the background.

---

## 8. Cache Observability

```
Metrics:
  cache.hit_rate          (target > 90%)
  cache.miss_rate         (alert > 20%)
  cache.eviction_rate     (alert > 5%)
  cache.memory_utilization (alert > 80%)
  cache.connection_count  (track growth)
  cache.latency_p99       (alert > 5ms)
```
