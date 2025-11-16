# Hustlehive Backend

A microservice-based e-commerce platform for student-to-student transactions.

## Architecture

- **Gateway Service**: Handles authentication, user management, and routes requests to other services.
- **Product Service**: Manages items, categories, images, and bids.

Both services use Go 1.22+, Gin framework, GORM ORM, SQLite databases, and communicate via REST HTTP.

## Prerequisites

- Go 1.22 or later installed on your system.
- Git for version control.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/davidberko36/Hustlehive_Backend.git
   cd Hustlehive_Backend
   ```

2. For each service, set up the environment:
   - Copy the example environment file: `cp .env.example .env`
   - Edit `.env` to set your own values (ensure JWT_SECRET is the same for both services).

3. Install dependencies for each service:
   ```
   cd gateway
   go mod tidy
   cd ../product-service
   go mod tidy
   cd ..
   ```

## Running the Services

1. Start the Product Service (in a separate terminal):
   ```
   cd product-service
   go run main.go
   ```
   The service will run on `http://localhost:8081`.

2. Start the Gateway Service (in another terminal):
   ```
   cd gateway
   go run main.go
   ```
   The service will run on `http://localhost:8080`.

## Testing the API

### Register a User
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password_hash": "password123",
    "full_name": "Test User",
    "address": "123 Test St",
    "phone": "123-456-7890",
    "profile_picture": "http://example.com/pic.jpg"
  }'
```

### Login
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```
This returns a JWT token. Copy it for the next requests.

### Create an Item (via Gateway Proxy)
```bash
curl -X POST http://localhost:8080/proxy/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Used Laptop",
    "description": "A great laptop for students",
    "price": 500.00,
    "quantity": 1,
    "is_auction": false,
    "start_price": 0,
    "start_date": "2025-11-04T00:00:00Z",
    "end_date": "2025-11-10T00:00:00Z",
    "status": "active"
  }'
```

### List Items
```bash
curl -X GET http://localhost:8080/proxy/items \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Services

### Gateway Service (Port 8080)
- **Purpose**: Authentication and request routing.
- **Endpoints**:
  - `POST /auth/register` - Register a new user.
  - `POST /auth/login` - Login and get JWT token.
  - `GET /auth/verify` - Verify JWT token.
  - `GET /proxy/items` - Proxy GET to Product Service.
  - `POST /proxy/items` - Proxy POST to Product Service.
  - `GET /proxy/items/:id` - Proxy GET single item.
  - `PUT /proxy/items/:id` - Proxy PUT item.
  - `DELETE /proxy/items/:id` - Proxy DELETE item.
  - `GET /proxy/categories` - Proxy GET categories.
  - `POST /proxy/categories` - Proxy POST category.
  - `GET /proxy/bids/:item_id` - Proxy GET bids.
  - `POST /proxy/bids` - Proxy POST bid.

### Product Service (Port 8081)
- **Purpose**: Item and bid management.
- **Endpoints**:
  - `GET /items` - List all items.
  - `GET /items/:id` - Get single item.
  - `POST /items` - Create item (authenticated).
  - `PUT /items/:id` - Update item (seller only).
  - `DELETE /items/:id` - Delete item (seller only).
  - `GET /categories` - List categories.
  - `POST /categories` - Create category.
  - `GET /bids/:item_id` - List bids for item.
  - `POST /bids` - Place a bid (authenticated).

## Inter-Service Communication

- Gateway verifies JWT and forwards authenticated requests to Product Service.
- Shared JWT secret for token validation.

## Extending the Platform

- Add Order Service for purchases.
- Add Review Service for ratings.
- Add Messaging Service for chat.
- Switch to PostgreSQL for production.
- Add API documentation with Swagger.

## Folder Structure

```
project-root/
├── .gitignore
├── README.md
├── gateway/
│   ├── .env.example
│   ├── main.go
│   ├── routes/
│   ├── controllers/
│   ├── middleware/
│   ├── models/
│   ├── database/
│   ├── utils/
│   └── gateway.db (ignored)
└── product-service/
    ├── .env.example
    ├── main.go
    ├── routes/
    ├── controllers/
    ├── middleware/
    ├── models/
    ├── database/
    ├── utils/
    └── product.db (ignored)
```

## Seeded databases (already included)

For convenience this repo includes a small seeder program that created demo SQLite databases used by the services:

- `gateway/gateway.db` — contains a demo user:
  - username: `demo`
  - password: `password123`

- `product-service/product.db` — contains sample data:
  - one category (`Electronics` / `Laptops`)
  - one item (`Demo Laptop`, seller_id = 1)
  - one image (for item 1)
  - one bid for item 1

These DB files were seeded using `scripts/tool.go` (run with `go run scripts/tool.go seed`). If you want to re-create the sample DBs, re-run that command.

## Quick start (run services)

Open two terminals (or tabs). In one run the Product Service, in the other the Gateway. Example commands (POSIX shell / cmd / most terminals):

1) Start Product Service (port 8081)

```bash
cd product-service
go run main.go
```

2) Start Gateway Service (port 8080)

```bash
cd gateway
go run main.go
```

Both services will use the seeded databases placed under `gateway/` and `product-service/`.

## Seeder and verification

To (re)seed the DBs or create them locally:

```bash
# from repo root
go run scripts/tool.go seed
```

To quickly verify the seeded rows (prints a sample user and item):

```bash
go run scripts/tool.go verify
```

## Sample requests

Use the seeded user to log in and get a JWT; then use the JWT to call proxy endpoints on the Gateway.

1) Login to obtain JWT

```bash
curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"password123"}' | jq
```

The response will be JSON with a `token` field. Save that token for subsequent requests.

2) Verify token

```bash
curl -s -X GET http://localhost:8080/auth/verify \
  -H "Authorization: Bearer <JWT_TOKEN>" | jq
```

3) List items (via gateway proxy)

```bash
curl -s -X GET http://localhost:8080/proxy/items \
  -H "Authorization: Bearer <JWT_TOKEN>" | jq
```

4) Get single item

```bash
curl -s -X GET http://localhost:8080/proxy/items/1 \
  -H "Authorization: Bearer <JWT_TOKEN>" | jq
```

5) Create an item (proxy)

```bash
curl -s -X POST http://localhost:8080/proxy/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "title":"New Phone",
    "description":"A used phone for students",
    "price":120.00,
    "quantity":1,
    "is_auction":false,
    "start_price":0,
    "start_date":"2025-11-08T00:00:00Z",
    "end_date":"2025-11-15T00:00:00Z",
    "status":"active"
  }' | jq
```

6) Place a bid (proxy)

```bash
curl -s -X POST http://localhost:8080/proxy/bids \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"item_id":1,"bid_amount":530.00}' | jq
```

Notes:
- If you don't have `jq` installed, omit the `| jq` at the end of the commands — JSON will still be printed.
- The Gateway forwards JWTs to the Product Service so protected product endpoints validate the same shared JWT secret.

If you'd like, I can also add a small cross-platform shell script to start both services concurrently (no PowerShell-only scripts) or add a Postman collection / OpenAPI file next.
 
## Wrapper scripts and Postman collection

I added simple wrapper scripts you can use to start both services and a Postman collection to import endpoints:

- `scripts/start_all.sh` — POSIX shell script that starts both services in background and writes logs to `./logs/`.
- `scripts/start_all.ps1` — PowerShell script that starts both services (Windows-friendly).
- `docs/postman_collection.json` — Postman collection (v2.1) with requests for login, verify, list items, get item, create item, and create bid. The login request stores the returned token into the Postman environment variable `token` so subsequent requests use it.

How to import the Postman collection

1. Open Postman.
2. Click Import -> File and select `docs/postman_collection.json`.
3. Create or select an Environment. Make sure the `baseUrl` variable is `http://localhost:8080` (the collection already has this default).
4. Run `Auth - Login` (it will save the `token` variable automatically in the environment via a small test script included in the request). If not saved automatically, copy the `token` from the response and set it manually in the environment variable `token`.
5. Run other requests (they use `Authorization: Bearer {{token}}`).

If you'd like an OpenAPI spec or a Postman collection with examples for request bodies and more advanced tests, I can expand the collection.

## Integrating services written in other languages

The Gateway is designed to be language-agnostic: any service (Node.js, Python, Ruby, Java, etc.) can be added as long as it exposes REST endpoints and follows a small contract. Below are recommended steps and best practices to integrate an external service with the Gateway.

1. Service contract (HTTP)
  - Expose stable REST endpoints (e.g. `/items`, `/orders`, `/health`).
  - Support JSON input and output, use consistent field names.
  - Provide a `/health` or `/ready` endpoint returning 200 when ready.

2. Authentication and JWT
  - The easiest option: share the Gateway's `JWT_SECRET` in the service's environment so the service can validate tokens directly.
  - Alternative (more secure): service calls Gateway verification endpoint (e.g., `GET /auth/verify`) with the token and rely on the Gateway to validate and return user claims.
  - Gateway forwards the Authorization header when proxying requests; make sure your service reads `Authorization: Bearer <token>`.

3. Environment variables and configuration
  - Keep service-specific config in a `.env` or config file (do NOT commit secrets). Use the `.env.example` pattern to document required settings.
  - Provide `SERVICE_PORT`, `DB_URL`, `JWT_SECRET` (if validating JWTs locally) in the environment.

4. Register the service with the Gateway (routing)
  - Update the Gateway's proxy/routes to forward paths to the new service URL (e.g., `http://localhost:8082`).
  - Example (pseudo): add `proxy.POST("/orders", controllers.ProxyOrders)` and have `controllers.ProxyOrders` forward to the new service.

5. CORS, rate limits, and headers
  - Gateway can enforce CORS and global rate limits; services should not duplicate global policies.
  - Services should accept forwarded client headers (e.g., `X-Forwarded-For`) if needed.

6. API documentation and OpenAPI
  - Publish an OpenAPI/Swagger spec for each service. The Gateway can reference or merge specs for centralized API docs.

7. Health checks and local development
  - Use the wrapper scripts (`scripts/start_all.*`) to start local services.
  - Add your service executable to `scripts/start_all.sh` / `.ps1` / `.bat` or create its own start script.

8. Example: adding a Python Flask service
  - Flask service exposes `/orders` and validates JWT using the shared `JWT_SECRET` (PyJWT).
  - Start Flask on port 8082, add Gateway proxy route `/proxy/orders` -> `http://localhost:8082/orders`.

9. Security note
  - Sharing `JWT_SECRET` is simple for local/dev. For production, prefer central auth (Gateway-only verification) or use public/private keys (RS256) so services can verify tokens without holding a symmetric secret.

10. Observability
  - Ensure services produce structured logs, health metrics, and optionally Prometheus metrics; the Gateway can aggregate traces and logs.

With these steps you can implement new services in any language and wire them into the Gateway with minimal changes. If you want, I can:
- add a small example service in Node.js or Python showing JWT validation and one endpoint, and
- extend `scripts/start_all.*` to optionally start that example service.
