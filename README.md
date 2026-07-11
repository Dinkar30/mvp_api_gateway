# High-Performance API Management Suite

This is a production-ready, cloud-native API Gateway designed to provide a unified security and  it also acts as observability layer for distributed microservices. It handles the "infrastructure concerns" (Authentication, Rate Limiting, Health Monitoring) so developers can primarily focus on building their stuff.

##  The Core Value

In a modern architecture, services shouldn't manage their own security. API Gateway sits as a **Transparent Proxy** in front of your services, offering:

- **Zero-Trust Security**: It is ensured that every request gets validated before it touches your backend.
- **Extreme Performance**: I have Implemented Redis-backed authentication caching and rate-limiting.
- **Operational Visibility**: Real-time traffic inspection and service health dashboards.

## Tech Stack

- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL (Relational Data), Redis (In-memory High-Speed Counters/Cache)
- **Security**: JWT (Dashboard Auth), Bcrypt (API Key Hashing), SHA-256 (Key Masking)
- **DevOps**: Docker, Docker Compose
- **Frontend**: Tailwind CSS, Jinja2 Templates

## Key Features

### 1. Universal Reverse Proxy

A content-agnostic "pipe" that forwards `GET`, `POST`, `PUT`, and `DELETE` requests to any registered backend. It handles headers, query params, and payloads transparently.

### 2. Multi-Tenant Role-Based Access Control (RBAC)

- **Admins**: Global visibility into all system traffic, service health, and user management.
- **Developers**: Self-service portal to register their own backends and generate unique API Keys.

### 3. Distributed Rate Limiting

Prevents API abuse using a "Fixed Window" algorithm implemented in Redis for sub-millisecond overhead. Limits are configurable per-user.

### 4. Self-Healing Health Monitor

A background worker performs active heartbeats on all registered services. If a service fails, gateway automatically trips a "Circuit Breaker," returning `503` errors to clients to prevent cascading failures.

### 5. High-Speed Auth Caching

To avoid database bottlenecks, the gateway caches verified API Key hashes in Redis with a configurable TTL, reducing authentication latency significantly.

## 📁 Architecture

```
Client -> [ API Gateway (Port 8000) ] -> [ Internal/External Backends ]
                 |               |
          [ Redis (Cache) ] [ Postgres (Storage) ]
```

## ⚙️ Quick Start

### 1. Clone and Launch

```bash
git clone https://github.com/your-username/api-gateway-suite.git
cd api-gateway-suite
docker-compose up --build
```

### 2. Initialize the Admin

```bash
docker-compose exec gateway python -m app.seed
```

This will generate your first Admin user and a master API Key.

### 3. Use the Dashboard

Navigate to `http://localhost:8000/auth/login` and log in with the credentials from the seed.

## 🛡 Security Implementation Note

This project follows industry best practices:

- **Bcrypt Hashing**: No plain-text keys or passwords are ever stored.
- **SHA-256 Pre-hashing**: Bypasses Bcrypt's 72-character limit for long API tokens.
- **HttpOnly Cookies**: Protects JWT sessions from XSS attacks.
- **CORS Middleware**: Enabled for secure cross-origin communication.

## 📈 Roadmap / Future Improvements

- **Request Retries**: Automatic 3-try logic for flaky GET requests.
- **Payload Logging**: Toggleable body inspection for debugging.
- **Prometheus Integration**: Exporting metrics for Grafana dashboards.