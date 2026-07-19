
# API Gateway Management Suite

A high-performance security and observability layer designed to sit in front of distributed microservices. This suite provides a unified entry point for authentication, rate limiting, and health monitoring, allowing developers to secure their backends with zero code changes to their core logic.

## The Core Work
The primary goal of this project was to solve the "Gateway Bottleneck" where security checks slow down traffic. 
Key implementations include:
- Implemented a SHA-256 pre-hashing layer to bypass Bcrypt’s native character limits for high-entropy API tokens.
- Built a Redis-backed authentication cache that stores verified session hashes, reducing auth overhead from disk-speed (DB) to sub-1ms (RAM).
- Migrated from SQLite to a fully containerized PostgreSQL environment with managed Docker volumes for persistent multi-tenant data.

## Tech Stack
- **Backend:** FastAPI (Python 3.13), SQLAlchemy 2.0 (Mapped Types)
- **Data:** PostgreSQL (Metadata / Logs), Redis (Rate limiting / Auth Cache)
- **Security:** PyJWT, Bcrypt, SHA-256
- **Infrastructure:** Docker, Nginx (Reverse Proxy + SSL)
- **Frontend:** Jinja2 Templates, Custom CSS

## Implemented Features
1. **Dynamic Reverse Proxy:** Content-agnostic forwarding for `GET`, `POST`, `PUT`, and `DELETE`.
2. **Multi-Tenant RBAC:** Distinct views for **Admins** (global visibility) and **Developers** (self-service key/service management).
3. **Redis Rate Limiting:** "Fixed Window" algorithm ensuring clients stay within their assigned quotas.
4. **Background Health Monitor:** Lifespan-based worker that performs active heartbeats and triggers 503 circuit breakers for failed services.
5. **Traffic Inspector:** Real-time logging of method, path, status codes, and exact latency.

---

## Developer Integration Guide

To secure your service with this gateway, follow these three steps:

### 1. Registration
1.  Sign up at `https://gatewayconsole.duckdns.org`.
2.  On the dashboard, click **"Generate New Key"**. Save this key immediately.
3.  Add your service:
    - **Prefix:** The URL keyword (e.g., `myservice`).
    - **Target URL:** Where your API is hosted (e.g., `https://my-app.render.com`).
    - **Health Path:** An endpoint returning 200 OK (e.g., `/`).

### 2. Update Frontend/Client
Point your API calls to the Gateway address instead of your raw server:
- **Pattern:** `https://gatewayconsole.duckdns.org/<prefix>/<endpoint>`
- **Header:** `X-API-KEY: <your-generated-key>`

```javascript
// Example Integration
const api = axios.create({
    baseURL: 'https://gatewayconsole.duckdns.org/social',
    headers: { 'X-API-KEY': 'gw_your_key_here' }
});
```

### 3. Enable the "Shield" (Backend Lockdown)
To prevent users from bypassing the gateway, Gateway attaches a `X-Shield` header to every proxied request. Add this middleware to your backend:

```javascript
// Express.js Example
app.use((req, res, next) => {
    if (req.headers['x-shield'] !== process.env.SECRET_PHRASE) {
        return res.status(403).json({ error: "Direct access forbidden." });
    }
    next();
});
```

---

## ⚙️ Local Development Setup (For learning and contribution purpose only)

### 1. Prerequisites
- Docker & Docker Compose
- A `.env` file containing: `DATABASE_URL`, `REDIS_HOST`, `JWT_SECRET`, and `SECRET_PHRASE`.

### 2. Launch
```bash
docker-compose -f docker-compose.prod.yml up --build
```

### 3. Initialize
```bash
docker compose exec gateway python -m app.seed
```

---

## ⚠️ Known Limitations & Vulnerabilities (To be worked on)
- **Payload Logging:** While the middleware captures request/response bodies, the UI modal for viewing large JSON strings is currently inconsistent.
- **Request Retries:** Automatic retries for failed GET requests are designed but not yet fully stress-tested for timeouts.
- **Role Elevation:** Admin roles must currently be set manually in the PostgreSQL database for security.
- **CORS Configuration:** Currently set to permissive (`"*"`) for prototype flexibility; requires strict origin mapping for production.

---

## 📈 Future Work 
- [ ] Implement Response Caching in Redis for static endpoints.
- [ ] Add Prometheus/Grafana exporters for system-level monitoring.
- [ ] Build a CLI tool for service management.

---
