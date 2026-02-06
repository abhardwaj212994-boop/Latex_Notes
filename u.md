# API Platform - End-to-End System Architecture & Design

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Authentication & Authorization](#authentication--authorization)
8. [Frontend Architecture](#frontend-architecture)
9. [Kong API Gateway Configuration](#kong-api-gateway-configuration)
10. [Security Design](#security-design)
11. [Performance Considerations](#performance-considerations)
12. [Deployment Architecture](#deployment-architecture)
13. [Design Decisions & Rationale](#design-decisions--rationale)
14. [Known Gaps & Future Enhancements](#known-gaps--future-enhancements)

---

## System Overview

The API Platform is a comprehensive API key management system that provides:
- **API Key Management**: Create, manage, and track API keys for accessing DocNexus APIs
- **Organization Management**: Multi-tenant organization structure with member management
- **Usage Tracking**: Monitor API usage and analytics
- **Gateway Integration**: Kong API Gateway integration for request validation and routing

### System Goals
1. Enable external clients to access DocNexus APIs via API keys
2. Provide self-service API key management through a web UI
3. Track and monitor API usage
4. Support multi-tenant organizations
5. Integrate seamlessly with existing DocNexus infrastructure

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
│              (Web UI, External API Clients, etc.)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Kong API Gateway (Port 8000)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Key-Auth Plugin: Validates X-API-Key header             │  │
│  │  Routes: /v5/profile, /v5/search                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────┬──────────────────────┘
             │                              │
             │ Validated Requests           │ Admin API
             │                              │
┌────────────▼──────────────┐   ┌──────────▼──────────────────────┐
│   docnexus-link (Port 80) │   │  API Key Service (Port 8080)   │
│                           │   │                                 │
│  • GET /v5/profile/us/:npi│   │  • POST /auth/token            │
│  • POST /v5/search        │   │  • CRUD /keys                  │
│  • Requires JWT auth       │   │  • CRUD /orgs                  │
│                           │   │  • GET /usage                  │
└───────────────────────────┘   └──────────┬──────────────────────┘
                                           │
                                           │ Database Queries
                                           │
                              ┌────────────▼──────────────────────┐
                              │   PostgreSQL Database            │
                              │                                 │
                              │  • api_keys                      │
                              │  • organizations                 │
                              │  • org_members                   │
                              │  • allowed_users                │
                              │  • usage_logs                   │
                              └─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    docnexus-frontend (Port 3000)                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Platform UI (/api-platform)                        │  │
│  │  • Overview, ApiKeys, Usage, Documentation, etc.        │  │
│  │  • Amplify Auth → JWT Token → API Key Service           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Proxy: /api-key-service
                             │
                             ▼
                    API Key Service (Port 8080)
```

---

## Component Details

### 1. Kong API Gateway

**Purpose**: Validates API keys and routes requests to upstream services.

**Configuration**:
- **Port**: 8000 (proxy), 8001 (admin API)
- **Database**: PostgreSQL (Kong's own database for configuration)
- **Plugins**: `key-auth` plugin enabled on docnexus-link service

**Key Design Decisions**:
- **Key-Auth Plugin**: Uses `X-API-Key` header for authentication
- **Route Paths**: Only `/v5/profile` and `/v5/search` (matches actual docnexus-link routes)
- **Strip Path**: `false` - preserves original path when forwarding
- **Service Discovery**: Static upstream URL configuration

**Routes Created**:
```
Service: docnexus-link
├── Route: /v5/profile → http://docnexus-link:80/v5/profile
└── Route: /v5/search → http://docnexus-link:80/v5/search
```

**Request Flow**:
1. Client sends request with `X-API-Key` header
2. Kong validates key against consumer credentials
3. If valid, forwards to docnexus-link
4. If invalid, returns 401 Unauthorized

### 2. API Key Service Backend

**Technology Stack**:
- **Framework**: FastAPI (async Python)
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Authentication**: JWT tokens

**Architecture Pattern**: RESTful API with dependency injection

**Key Components**:

#### 2.1 Database Layer (`app/database.py`)
```python
# Connection Pooling Configuration
pool_size=10          # Base connection pool size
max_overflow=20       # Additional connections allowed
pool_pre_ping=True    # Verify connections before use
pool_recycle=3600     # Recycle connections after 1 hour
```

**Rationale**:
- **pool_size=10**: Handles moderate concurrent requests
- **max_overflow=20**: Allows burst traffic up to 30 total connections
- **pool_pre_ping**: Prevents stale connection errors
- **pool_recycle**: Prevents long-lived connection issues

#### 2.2 Models (`app/models.py`)
- **AllowedUser**: Users authorized to access API Key Service
- **Organization**: Multi-tenant organizations
- **OrgMember**: Organization membership with roles
- **APIKey**: API keys with hashed storage
- **UsageLog**: API usage tracking

**Indexes**:
- `ix_usage_logs_key_requested`: Composite index on (key_id, requested_at) for efficient usage queries
- `ix_org_members_org_email`: Unique constraint on (org_id, email)
- `ix_api_keys_key_hash`: Unique index for key lookup

#### 2.3 Routers

**Auth Router** (`/auth`):
- `POST /auth/token`: Exchange Amplify email for JWT token
- Validates user is in `allowed_users` table
- Returns JWT with 7-day expiration

**Keys Router** (`/keys`):
- `POST /keys`: Create new API key
  - Generates key: `dnx_dev_{random_32_chars}`
  - Hashes key with SHA-256
  - Creates Kong consumer
  - Adds key-auth credential to Kong
  - Returns plain key once (never stored)
- `GET /keys`: List user's API keys
- `GET /keys/{id}`: Get specific key (no plain key returned)
- `DELETE /keys/{id}`: Deactivate key
- `PATCH /keys/{id}/toggle`: Toggle active status

**Organizations Router** (`/orgs`):
- `POST /orgs`: Create organization
- `GET /orgs`: List user's organizations
- `GET /orgs/{id}`: Get organization details
- `GET /orgs/{id}/members`: List members
- `POST /orgs/{id}/members`: Add member (admin only)
- `DELETE /orgs/{id}/members/{member_id}`: Remove member (admin only)

**Usage Router** (`/usage`):
- `GET /usage`: Get usage logs with filtering
- `GET /usage/stats`: Get aggregated statistics

### 3. docnexus-link Backend

**Current State**: Existing FastAPI service with v5 routes

**Routes**:
- `GET /v5/profile/us/{npi_number}`: Get US provider profile
- `POST /v5/search`: Search for healthcare professionals

**Authentication**: Currently requires JWT via `get_current_user` dependency

**Known Gap**: Kong validates API keys but doesn't convert to JWT. External API-key-only clients will get 401 unless docnexus-link is updated to accept Kong-validated requests.

### 4. Frontend (docnexus-frontend)

**Technology Stack**:
- React with TypeScript
- Material-UI (MUI)
- Vite build tool
- AWS Amplify for authentication

**API Platform UI Structure**:
```
src/pages/Dashboard/ApiPlatform/
├── ApiPlatform.tsx          # Main container with tabs
├── Overview.tsx            # Dashboard overview
├── ApiKeys.tsx             # Key management UI
├── Usage.tsx               # Usage logs and stats
├── Documentation.tsx        # API documentation
├── Settings.tsx            # Settings (placeholder)
├── OrgAdmin.tsx            # Organization management
└── useApiKeyServiceAuth.ts  # Auth hook
```

**Authentication Flow**:
1. User signs in with Amplify
2. `useApiKeyServiceAuth` hook:
   - Extracts email from Amplify session
   - Calls `POST /auth/token` with email
   - Receives JWT token
   - Stores in localStorage
3. All API calls include `Authorization: Bearer <jwt>` header

**Service Layer** (`src/services/apiKeyService.ts`):
- Centralized API client
- Type-safe interfaces
- Error handling
- Automatic token injection from localStorage

**Vite Proxy Configuration**:
```typescript
proxy: {
  "/api-key-service": {
    target: "http://localhost:8080",
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api-key-service/, ""),
  },
}
```

**Rationale**: Allows frontend to call `/api-key-service/*` which proxies to backend, avoiding CORS issues in development.

---

## Data Flow

### API Key Creation Flow

```
1. User clicks "Create API Key" in UI
   ↓
2. Frontend calls POST /keys with name and org_id
   ↓
3. API Key Service:
   a. Validates user is member of org
   b. Generates random key: dnx_dev_{32_chars}
   c. Hashes key with SHA-256
   d. Creates Kong consumer via Admin API
   e. Adds key-auth credential to Kong consumer
   f. Stores hash in database (never plain key)
   g. Returns plain key to frontend (one-time)
   ↓
4. Frontend displays key with copy button
   ↓
5. User copies key (never shown again)
```

### API Request Flow (External Client)

```
1. External client sends request:
   curl -H "X-API-Key: dnx_dev_xxx" http://kong:8000/v5/profile/us/1234567890
   ↓
2. Kong receives request
   ↓
3. Kong key-auth plugin:
   a. Extracts X-API-Key header
   b. Looks up consumer by key
   c. If found, adds consumer info to headers
   d. If not found, returns 401
   ↓
4. Kong routes to docnexus-link:80
   ↓
5. docnexus-link receives request
   ↓
6. docnexus-link checks for JWT (get_current_user)
   ↓
7. ❌ ISSUE: No JWT present, returns 401
   (This is a known gap - docnexus-link needs update)
```

### Frontend Authentication Flow

```
1. User navigates to /api-platform
   ↓
2. useApiKeyServiceAuth hook executes
   ↓
3. Checks localStorage for token
   ↓
4. If not found:
   a. Gets Amplify session
   b. Extracts email from idToken
   c. Calls POST /auth/token with email
   d. Receives JWT token
   e. Stores in localStorage
   ↓
5. All API calls include Authorization header
   ↓
6. API Key Service validates JWT:
   a. Decodes JWT
   b. Extracts email
   c. Checks allowed_users table
   d. Returns user object
```

---

## Database Design

### Schema Overview

```sql
-- Users allowed to access API Key Service
allowed_users
├── id (PK)
├── email (UNIQUE, INDEXED)
├── created_at
└── updated_at

-- Organizations (multi-tenant)
organizations
├── id (PK)
├── name (INDEXED)
├── created_at
└── updated_at

-- Organization members
org_members
├── id (PK)
├── org_id (FK → organizations.id, CASCADE DELETE)
├── email (INDEXED)
├── role ('admin' | 'member')
├── created_at
└── updated_at
└── UNIQUE(org_id, email) -- Composite unique constraint

-- API Keys
api_keys
├── id (PK)
├── org_id (FK → organizations.id, CASCADE DELETE)
├── name
├── key_hash (UNIQUE, INDEXED) -- SHA-256 hash, never plain text
├── kong_consumer_id (INDEXED) -- Kong consumer UUID
├── is_active (INDEXED)
├── created_by (email)
├── created_at
├── updated_at
└── last_used_at

-- Usage Logs
usage_logs
├── id (PK)
├── key_id (FK → api_keys.id, CASCADE DELETE)
├── endpoint
├── requested_at (INDEXED with key_id)
├── response_status
├── response_time_ms
├── request_data (TEXT)
└── response_data (TEXT)
└── INDEX(key_id, requested_at) -- Composite index for queries
```

### Design Decisions

1. **Key Hashing**: API keys are hashed with SHA-256 before storage. Plain keys are never stored in database.

2. **Cascade Deletes**: 
   - Deleting organization deletes all members and keys
   - Deleting API key deletes all usage logs
   - Prevents orphaned records

3. **Composite Indexes**:
   - `(key_id, requested_at)`: Optimizes usage queries filtered by key and date range
   - `(org_id, email)`: Ensures unique membership per org

4. **No Soft Deletes**: Keys are deactivated (`is_active=false`) rather than deleted. This allows:
   - Audit trail preservation
   - Usage log retention
   - Ability to reactivate if needed

5. **Usage Logs Design**:
   - Stores request/response data as TEXT (JSON strings)
   - No TTL or archival (known gap)
   - Indexed for efficient querying by key and date

---

## API Design

### RESTful Conventions

**Resource Naming**:
- `/keys` - API keys collection
- `/orgs` - Organizations collection
- `/usage` - Usage logs collection
- `/auth` - Authentication endpoints

**HTTP Methods**:
- `GET`: Retrieve resources
- `POST`: Create resources
- `PATCH`: Partial updates
- `DELETE`: Remove resources

**Status Codes**:
- `200 OK`: Successful GET/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid auth
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Request/Response Formats

**Create API Key**:
```http
POST /keys
Content-Type: application/json
Authorization: Bearer <jwt>

{
  "name": "Production Key",
  "org_id": 1,
  "endpoint_groups": []
}

Response: 201 Created
{
  "id": 1,
  "name": "Production Key",
  "org_id": 1,
  "key": "dnx_dev_abc123...",  // Only returned on creation
  "is_active": true,
  "created_by": "user@example.com",
  "created_at": "2026-02-06T00:00:00Z",
  "last_used_at": null
}
```

**List API Keys**:
```http
GET /keys?org_id=1
Authorization: Bearer <jwt>

Response: 200 OK
[
  {
    "id": 1,
    "name": "Production Key",
    "org_id": 1,
    "is_active": true,
    "created_by": "user@example.com",
    "created_at": "2026-02-06T00:00:00Z",
    "last_used_at": "2026-02-06T12:00:00Z"
  }
]
```

**Note**: Plain API key is never returned after creation.

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Authentication & Authorization

### Two-Tier Authentication System

#### Tier 1: Frontend → API Key Service
- **Method**: JWT tokens
- **Flow**: Amplify email → JWT token → API Key Service
- **Storage**: JWT in localStorage
- **Validation**: JWT signature + user in `allowed_users` table
- **Expiration**: 7 days

#### Tier 2: External Clients → Kong → docnexus-link
- **Method**: API keys (X-API-Key header)
- **Flow**: API key → Kong validation → docnexus-link
- **Storage**: Key-auth credentials in Kong
- **Validation**: Kong key-auth plugin
- **Issue**: docnexus-link still requires JWT (known gap)

### Authorization Model

**Organization-Based Access Control**:
- Users belong to organizations via `org_members` table
- Users can only see/manage keys for their organizations
- Admin role can add/remove members
- Member role can create/manage keys

**Permission Matrix**:
| Action | Admin | Member |
|--------|-------|--------|
| View org keys | ✅ | ✅ |
| Create keys | ✅ | ✅ |
| Delete own keys | ✅ | ✅ |
| Delete others' keys | ✅ | ❌ |
| Add members | ✅ | ❌ |
| Remove members | ✅ | ❌ |

### Security Considerations

1. **API Key Security**:
   - Keys are hashed before storage (SHA-256)
   - Plain keys shown only once on creation
   - Keys cannot be retrieved after creation
   - Keys can be deactivated but not deleted

2. **JWT Security**:
   - Secret key stored in environment variable
   - 7-day expiration
   - Email-based claims (no sensitive data)

3. **Database Security**:
   - Connection pooling prevents connection exhaustion
   - Parameterized queries prevent SQL injection
   - CASCADE deletes prevent orphaned records

---

## Frontend Architecture

### Component Hierarchy

```
ApiPlatform (Container)
├── Tabs Navigation
├── Overview Tab
│   └── Stats Cards, Quick Start
├── ApiKeys Tab
│   ├── Key List Table
│   ├── Create Dialog
│   └── Delete/Toggle Actions
├── Usage Tab
│   ├── Stats Cards
│   └── Usage Logs Table
├── Documentation Tab
│   └── API Documentation
├── Settings Tab
│   └── (Placeholder)
└── OrgAdmin Tab
    ├── Organization List
    ├── Member Management
    └── Create Org/Member Dialogs
```

### State Management

**Local State**: React `useState` for component-level state
**Server State**: Direct API calls with loading/error states
**Auth State**: `useApiKeyServiceAuth` hook manages JWT token

**Rationale**: No Redux/Zustand needed for current scope. Direct API calls with hooks provide sufficient state management.

### Error Handling

- **Network Errors**: Caught in service layer, displayed as alerts
- **Auth Errors**: Redirect to login or show error message
- **Validation Errors**: Display inline with form fields
- **Server Errors**: Generic error messages to users

### UI/UX Patterns

1. **Loading States**: CircularProgress during async operations
2. **Error States**: Alert components with dismiss
3. **Success States**: Success alerts for key creation
4. **Empty States**: Helpful messages when no data
5. **Confirmation Dialogs**: Confirm destructive actions

---

## Kong API Gateway Configuration

### Service Configuration

```yaml
Service: docnexus-link
  URL: http://docnexus-link:80
  Protocol: http
  Connect Timeout: 60000
  Write Timeout: 60000
  Read Timeout: 60000
```

### Plugin Configuration

```yaml
Plugin: key-auth
  Service: docnexus-link
  Config:
    key_names: ["X-API-Key"]
    hide_credentials: true
    key_in_header: true
    key_in_query: false
    key_in_body: false
```

**Rationale**:
- `hide_credentials: true`: Removes API key from headers before forwarding
- `key_names: ["X-API-Key"]`: Standard header name
- Only header-based auth (no query/body) for security

### Route Configuration

```yaml
Route: docnexus-link-profile
  Service: docnexus-link
  Paths: ["/v5/profile"]
  Strip Path: false
  Methods: ["GET", "POST"]
  Preserve Host: false

Route: docnexus-link-search
  Service: docnexus-link
  Paths: ["/v5/search"]
  Strip Path: false
  Methods: ["POST"]
  Preserve Host: false
```

**Design Decisions**:
- **Strip Path: false**: Preserves `/v5/profile` path when forwarding
- **Specific Paths**: Only routes that exist in docnexus-link
- **No Wildcards**: Explicit paths for security

### Bootstrap Process

1. Create service (or update if exists)
2. Enable key-auth plugin on service
3. Create routes for `/v5/profile` and `/v5/search`
4. Verify routes are active

**Idempotency**: Script handles existing resources gracefully (409 responses)

---

## Security Design

### Defense in Depth

1. **Network Layer**:
   - Kong validates API keys before routing
   - Only validated requests reach backend services

2. **Application Layer**:
   - JWT validation for API Key Service
   - Organization-based access control
   - Input validation on all endpoints

3. **Data Layer**:
   - API keys hashed before storage
   - Parameterized queries prevent SQL injection
   - Connection pooling prevents DoS

4. **Infrastructure Layer**:
   - Environment variables for secrets
   - CORS restrictions
   - HTTPS in production (assumed)

### API Key Security

**Generation**:
- Cryptographically secure random (secrets.token_urlsafe)
- 32-character random component
- Prefix: `dnx_dev_` for identification

**Storage**:
- SHA-256 hash stored in database
- Plain key never stored
- Hash used for lookup (if needed)

**Transmission**:
- Sent over HTTPS (production)
- Stored in Kong key-auth credentials
- Never logged or exposed in error messages

**Lifecycle**:
- Created with organization context
- Can be deactivated (not deleted)
- Usage tracked for monitoring

### JWT Security

**Token Structure**:
```json
{
  "sub": "user@example.com",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Security Features**:
- Email-based subject (no sensitive data)
- 7-day expiration
- HS256 algorithm
- Secret key from environment

**Storage**:
- localStorage (frontend)
- Not httpOnly (needed for API calls)
- Risk: XSS vulnerability (mitigated by React sanitization)

### Database Security

**Connection Security**:
- Connection pooling prevents exhaustion
- Pool pre-ping verifies connections
- Connection recycling prevents stale connections

**Query Security**:
- SQLAlchemy ORM prevents SQL injection
- Parameterized queries for all operations
- No raw SQL queries

**Access Control**:
- Database user has minimal required permissions
- No superuser access
- Separate database for Kong (isolation)

---

## Performance Considerations

### Database Optimization

1. **Connection Pooling**:
   - Base pool: 10 connections
   - Max overflow: 20 connections
   - Total capacity: 30 concurrent connections
   - Prevents connection exhaustion

2. **Indexes**:
   - `ix_usage_logs_key_requested`: Composite index for usage queries
   - `ix_api_keys_key_hash`: Unique index for key lookup
   - `ix_org_members_org_email`: Unique constraint with index

3. **Query Optimization**:
   - Eager loading relationships where needed
   - Pagination on usage logs (limit/offset)
   - Filtered queries reduce data transfer

### API Performance

1. **Async Operations**:
   - FastAPI async/await for I/O operations
   - Non-blocking database queries
   - Concurrent request handling

2. **Caching** (Future):
   - JWT validation could be cached
   - Organization membership cached
   - Kong consumer lookup cached

3. **Rate Limiting** (Future):
   - Per-key rate limits
   - Per-organization rate limits
   - Global rate limits

### Frontend Performance

1. **Code Splitting**:
   - Route-based code splitting
   - Lazy loading of API Platform components

2. **API Calls**:
   - Parallel API calls where possible
   - Debouncing on search/filter inputs
   - Optimistic updates for better UX

---

## Deployment Architecture

### Local Development

```
┌─────────────────────────────────────────┐
│  Docker Compose (api-platform/)        │
│  ├── kong-database (PostgreSQL)         │
│  ├── kong-migrations (one-time)        │
│  ├── kong (API Gateway)                 │
│  ├── api-key-service-db (PostgreSQL)    │
│  └── api-key-backend (FastAPI)         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Local Services                         │
│  ├── docnexus-link (uvicorn :80)       │
│  └── docnexus-frontend (vite :3000)   │
└─────────────────────────────────────────┘
```

### Production Deployment

```
┌─────────────────────────────────────────┐
│  Load Balancer / Reverse Proxy         │
│  (HTTPS termination, SSL certificates) │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────────┐   ┌──────▼──────────┐
│  Kong        │   │  Frontend       │
│  (Port 8000) │   │  (Static Files) │
└───┬──────────┘   └─────────────────┘
    │
    ├──────────────┬─────────────────┐
    │              │                 │
┌───▼──────┐  ┌───▼──────────┐  ┌───▼──────────┐
│ docnexus │  │ API Key       │  │ PostgreSQL   │
│ -link    │  │ Service       │  │ (RDS)        │
│ (Port 80)│  │ (Port 8080)   │  │              │
└──────────┘  └───────┬───────┘  └──────────────┘
                      │
                      │
              ┌───────▼───────┐
              │ PostgreSQL    │
              │ (Kong DB)     │
              └───────────────┘
```

### Environment Variables

**API Key Service Backend**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
KONG_ADMIN_URL=http://kong:8001
JWT_SECRET_KEY=<strong-random-secret>
ALLOWED_ORIGINS=https://app.docnexus.ai,https://www.docnexus.ai
```

**Kong**:
```bash
KONG_PG_HOST=postgres-host
KONG_PG_USER=kong
KONG_PG_PASSWORD=<password>
KONG_PG_DATABASE=kong
```

**Frontend**:
```bash
VITE_API_KEY_SERVICE_URL=/api-key-service  # or full URL
VITE_COGNITO_USER_POOL_ID=<pool-id>
VITE_COGNITO_CLIENT_ID=<client-id>
VITE_COGNITO_DOMAIN=<domain>
```

### Deployment Steps

1. **Database Setup**:
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Seed initial data
   python -m scripts.seed
   ```

2. **Kong Setup**:
   ```bash
   # Bootstrap Kong
   ./scripts/kong-bootstrap.sh
   ```

3. **Service Deployment**:
   - Deploy Kong (port 8000)
   - Deploy API Key Service (port 8080)
   - Deploy docnexus-link (port 80)
   - Deploy frontend (static files)

4. **Health Checks**:
   - Kong: `GET http://kong:8001/`
   - API Key Service: `GET http://api-key-service:8080/health`
   - docnexus-link: `GET http://docnexus-link:80/v5/health`

---

## Design Decisions & Rationale

### 1. Why Kong API Gateway?

**Decision**: Use Kong for API key validation and routing

**Rationale**:
- Industry-standard API gateway
- Built-in key-auth plugin
- Easy integration with existing services
- Admin API for programmatic configuration
- Supports rate limiting, logging (future)

**Alternatives Considered**:
- Custom middleware: More maintenance overhead
- AWS API Gateway: Vendor lock-in, higher cost
- Traefik: Less mature plugin ecosystem

### 2. Why Separate API Key Service?

**Decision**: Separate FastAPI service for key management

**Rationale**:
- Separation of concerns (key management vs. API logic)
- Independent scaling
- Different authentication (JWT vs. API keys)
- Easier to maintain and test
- Can be reused for other APIs

**Alternatives Considered**:
- Integrate into docnexus-link: Tight coupling, harder to scale
- Microservice per feature: Over-engineering for current needs

### 3. Why JWT for Frontend Auth?

**Decision**: JWT tokens for frontend → API Key Service authentication

**Rationale**:
- Stateless authentication
- No session storage needed
- Works well with Amplify integration
- 7-day expiration reduces refresh frequency
- Standard pattern for API authentication

**Alternatives Considered**:
- Session-based: Requires session storage, more complex
- OAuth2: Overkill for internal UI
- API keys for UI: Less secure, harder to revoke

### 4. Why Hash API Keys?

**Decision**: SHA-256 hash before database storage

**Rationale**:
- Security best practice
- Prevents key exposure if database compromised
- One-way hash (cannot reverse)
- Fast lookup still possible (if needed)

**Alternatives Considered**:
- Encryption: Reversible, but adds complexity
- Plain storage: Security risk
- Key derivation: Overkill for this use case

### 5. Why Organization-Based Multi-Tenancy?

**Decision**: Organizations own API keys, users belong to organizations

**Rationale**:
- Natural grouping for enterprise customers
- Role-based access control (admin/member)
- Usage tracking per organization
- Billing/quotas per organization (future)

**Alternatives Considered**:
- User-only: Doesn't scale for teams
- Global keys: No isolation
- Project-based: More complex, not needed yet

### 6. Why Async SQLAlchemy?

**Decision**: Use async SQLAlchemy with asyncpg driver

**Rationale**:
- Non-blocking I/O for better concurrency
- FastAPI async support
- Better performance under load
- Modern Python async patterns

**Alternatives Considered**:
- Sync SQLAlchemy: Simpler but less performant
- Raw asyncpg: More boilerplate
- Tortoise ORM: Less mature ecosystem

### 7. Why Alembic Migrations?

**Decision**: Use Alembic instead of `create_all()`

**Rationale**:
- Version control for schema changes
- Production-safe migrations
- Rollback capability
- Team collaboration on schema

**Alternatives Considered**:
- `create_all()`: Not production-safe, no versioning
- Manual SQL: Error-prone, no versioning
- Django migrations: Not compatible with FastAPI

### 8. Why Connection Pooling?

**Decision**: Configure connection pool (pool_size=10, max_overflow=20)

**Rationale**:
- Prevents connection exhaustion
- Reuses connections (performance)
- Handles burst traffic
- Production best practice

**Alternatives Considered**:
- No pooling: Connection exhaustion under load
- Larger pool: Wastes resources
- Smaller pool: Limits concurrency

### 9. Why Composite Indexes?

**Decision**: Index on `(key_id, requested_at)` for usage logs

**Rationale**:
- Optimizes common query pattern
- Filters by key_id, then sorts by date
- Significantly faster queries
- Minimal write overhead

**Alternatives Considered**:
- Single column indexes: Less efficient
- No indexes: Slow queries on large tables
- More indexes: Write overhead

### 10. Why Vite Proxy?

**Decision**: Proxy `/api-key-service` to backend in development

**Rationale**:
- Avoids CORS issues
- Matches production routing
- Simple configuration
- No code changes needed

**Alternatives Considered**:
- CORS headers: More complex, security concerns
- Different URLs: Inconsistent dev/prod
- No proxy: CORS errors in development

---

## Known Gaps & Future Enhancements

### Current Gaps

1. **JWT Requirement in docnexus-link**
   - **Issue**: docnexus-link requires JWT, but Kong only validates API keys
   - **Impact**: External API-key-only clients get 401
   - **Solution**: Update docnexus-link to accept Kong-validated requests
   - **Workaround**: None currently

2. **Usage Logging Not Implemented**
   - **Issue**: UsageLog table exists but not populated
   - **Impact**: No usage tracking
   - **Solution**: Implement Kong plugin or middleware to log usage
   - **Priority**: Medium

3. **No Usage Retention Policy**
   - **Issue**: usage_logs can grow unbounded
   - **Impact**: Database bloat over time
   - **Solution**: Implement TTL or archival strategy
   - **Priority**: Low (short-term)

### Future Enhancements

1. **Rate Limiting**
   - Per-key rate limits
   - Per-organization quotas
   - Burst handling
   - Implementation: Kong rate-limiting plugin

2. **Usage Analytics**
   - Dashboard with charts
   - Endpoint-level analytics
   - Time-series data
   - Export capabilities

3. **Key Rotation**
   - Automatic key rotation
   - Grace period for old keys
   - Notification system

4. **Webhooks**
   - Usage threshold alerts
   - Key expiration warnings
   - Organization events

5. **API Versioning**
   - Versioned endpoints
   - Deprecation notices
   - Migration guides

6. **Enhanced Security**
   - IP whitelisting per key
   - Key expiration dates
   - Audit logging
   - Two-factor authentication

7. **Billing Integration**
   - Usage-based billing
   - Invoice generation
   - Payment processing

8. **Developer Portal**
   - Self-service signup
   - API documentation
   - Interactive API explorer
   - SDK generation

---

## Conclusion

This architecture provides a solid foundation for API key management with:
- ✅ Secure key generation and storage
- ✅ Multi-tenant organization support
- ✅ Kong integration for request validation
- ✅ Self-service UI for key management
- ✅ Scalable, production-ready design

The system is designed to evolve, with clear extension points for future enhancements while maintaining security and performance.
