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



## Developer's Guide 
Gateway console is more than just a proxy, it is a security shield for your microservices. This guide explains how to integrate your existing sevices and secure them against direct attacks.

### 1. Onboard your Service
1. Navigate to the signup page and create your developer profile , now login and you will be redirected to the dashboard
2. **Generate API Key**: In the dashboard , click "Generate New Key". Save this key as this key is vital in authorizing your requests.
3. Register Service:
  - **Prefix**: Choose a keyword , try to keep it short
  - **Target URL**: The internal/private URL of your app (e.g., https://my-backend.render.com).
  - **Health Path**: An endpoint that returns 200 OK (e.g., /).
Thus your service is now onboarded 
### 2. Using the Gateway
Instead of calling your backend API directly, prefix your paths in your frontend with the Gateway address.
- **Old URL**: 
```bash
https://your-api.com
```
- **New URL**:
```bash
http://16.192.94.81/<your-prefix>/<endpoint>
```
**Header required**:
```
X-API-KEY: <your-generated-apikey>
```
example:
```bash
const api = axios.create({
    baseURL: 'http://16.192.94.81/social', // Your Gateway IP + Prefix
    headers: {
        'X-API-KEY': 'your_generated_api_key' // The key you got from your Dashboard
    }
});
```

### 3. Enabling Protection
In order to prevent users from bypassing the gateway and hitting your server directly , add a check to your backend for X-Shield header.
- The gateway console automatically attaches this header to every request it proxies , incase this header is missing or incorrect , your backend rejects the  incoming request with a 403 forbidden
```bash
app.use((req, res, next) => {
    // We only allow requests that have the Gateway's Secret Shield Header
    if (req.headers['x-shield'] !== "SUPER_SECRET_PASSPHRASE") {
        return res.status(403).json({ error: "Access Denied: Direct traffic forbidden." });
    }
    next();
});
```