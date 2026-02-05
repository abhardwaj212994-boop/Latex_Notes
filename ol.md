# DocNexus API Platform — Architecture, Flow & Decisions

This document describes the API key management system end-to-end: local setup (with non-colliding ports), production flow, and every major design decision.

---

## Table of contents

1. [Overview](#1-overview)
2. [Local development ports (no collisions)](#2-local-development-ports-no-collisions)
3. [Components](#3-components)
4. [Data flow (local and production)](#4-data-flow-local-and-production)
5. [Production deployment flow](#5-production-deployment-flow)
6. [Design decisions](#6-design-decisions)
7. [Environment variables reference](#7-environment-variables-reference)
8. [Quick start (local)](#8-quick-start-local)
9. [Related docs](#9-related-docs)

---

## 1. Overview

The **DocNexus API Platform** provides:

- **API key lifecycle**: Create, list, update, delete keys per organization; keys are scoped to an org and have environment (production / development / testing), rate limits, and allowed endpoints.
- **Organization and permissions**: Orgs have members with one of two roles — **admin** (full key CRUD and endpoint permissions) or **member** (can only edit which endpoints a key can access).
- **Usage tracking**: Per-org and per-key request counts, latency, errors, and recent activity for dashboards.
- **Gateway**: Kong validates API keys and routes traffic to the DocNexus backend (docnexus-link); rate limiting is applied at the gateway or per-key.
- **UI**: Integrated in docnexus-frontend (Overview, API Keys, Usage, Documentation, Organizations, Settings).
- **SDK**: JavaScript/TypeScript client that sends the API key with each request.

All external API traffic (Script Lift, HCP Profiles) can go through the gateway with a single API key; the backend does not need to implement key storage or validation.

---

## 2. Local development ports (no collisions)

Ports are chosen so that **docnexus-link**, **API Key Service**, **Kong**, and the **frontend** can run on the same machine without conflict.

| Component            | Port | Purpose |
|----------------------|------|--------|
| **docnexus-link**    | 8000 | Backend API (v5 + v1 gateway routes). When Kong is not used, clients call this directly. |
| **API Key Service**  | 8002 | Orgs, keys, usage, key validation. Used by the UI and (optionally) Kong. |
| **docnexus-frontend**| 3000 | Vite dev server. |
| **Kong proxy**       | 8010 | Public gateway when Kong is used. Forwards to docnexus-link:8000. |
| **Kong admin**      | 8011 | Kong Admin API (config, consumers). Used by scripts or API Key Service to sync consumers. |

- **Without Kong**: SDK and curl call `http://localhost:8000` (docnexus-link).
- **With Kong**: SDK and curl call `http://localhost:8010` (Kong); Kong forwards to `http://host.docker.internal:8000` (docnexus-link on the host).

No two services share a port.

---

## 3. Components

### 3.1 API Key Service (`api-key-service/`)

- **Stack**: FastAPI, SQLAlchemy (SQLite for dev, Postgres for prod).
- **Responsibilities**:
  - Organizations and members (admin / member roles).
  - API key CRUD; key hashing (SHA-256), prefix/suffix for display (e.g. `dnx_prod_****************3456`).
  - Usage: overview, daily series, per-key breakdown, recent activity; optional log endpoint for recording requests.
  - Key validation endpoint for gateways: `GET /api/v1/validate` with `X-API-Key`; returns 200 + rate-limit headers or 401.
- **Auth (current)**: `X-User-Email` header to resolve the current user’s org (dev). Production should use JWT from Cognito (or your IdP) and map to org.
- **Run locally**: `./run.sh` (creates venv, installs deps, listens on **8002**).

### 3.2 Kong (`kong/`)

- **Role**: API gateway in front of docnexus-link: key-auth, rate-limiting, routing.
- **Config**: DB-less declarative `kong.yml`; routes for `/v1/script-lift`, `/v5/search`, `/v1/hcp-profiles`, `/v5/profile` → upstream `http://host.docker.internal:8000`.
- **Local ports**: Proxy **8010**, Admin **8011** (see [§2](#2-local-development-ports-no-collisions)).
- **Production**: Typically Kong with a database; consumers/credentials created via Admin API when keys are created in the API Key Service.

### 3.3 docnexus-link (`docnexus-link/`)

- **Role**: Backend API (v5 search, profile, etc.) and **v1 gateway routes** (`/v1/hcp-profiles/:npi`, `/v1/script-lift/analyze`) for Kong.
- **Local port**: **8000**.
- **Run locally**: `./run.sh` (venv, uvicorn on 8000).

### 3.4 docnexus-frontend (`docnexus-frontend/`)

- **API Platform UI**: Routes under `/api-platform` (Overview, API Keys, Usage, Documentation, Organizations, Settings). Calls the API Key Service at `VITE_API_KEY_SERVICE_URL` (default **http://localhost:8002**).
- **Auth**: Cognito (env: `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_DOMAIN`). For API Key Service, dev uses `window.__API_PLATFORM_USER_EMAIL__`; production should send the Cognito user’s email (or JWT) so the API Key Service can resolve the org.
- **Local port**: **3000** (Vite).

### 3.5 docnexus SDK (`docnexus-sdk/`)

- **Role**: JS/TS client; sends API key on every request (`X-API-Key` / `Api-Key`).
- **Usage**: `new DocNexus({ apiKey, baseUrl })`; `baseUrl` is the **gateway** (e.g. Kong at **https://api.docnexus.ai** in prod, or **http://localhost:8010** with Kong locally, or **http://localhost:8000** when calling docnexus-link directly).

---

## 4. Data flow (local and production)

### 4.1 User opens API Platform UI

1. User signs in to the app (Cognito).
2. User navigates to `/api-platform`. Frontend loads Overview, Keys, Usage, etc.
3. Frontend sends requests to the **API Key Service** (e.g. `http://localhost:8002` locally). Each request includes:
   - **Dev**: `X-User-Email` (set via `window.__API_PLATFORM_USER_EMAIL__` or from Cognito).
   - **Prod**: Should send Cognito JWT or a header derived from it (e.g. email) so the API Key Service can resolve the org.
4. API Key Service looks up the user’s org (by email or JWT claim), enforces admin vs member permissions, and returns keys/usage/orgs.

### 4.2 User creates an API key

1. User clicks “Create Key” in the UI (or calls `POST /api/v1/keys` with name and environment).
2. API Key Service checks that the user is an **admin** of the org.
3. Service generates a secret (e.g. `dnx_test_<random>`), stores its hash and metadata (rate limits, allowed endpoints), and returns the **full key once** in the response.
4. (Optional) In production, a job or the service calls Kong Admin API to create a **consumer** and attach the key as a credential and set rate-limiting; then all traffic for that key goes through Kong.

### 4.3 Client (SDK or curl) calls the API

**Path A — Through Kong (production or local with Kong):**

1. Client sends a request to the **gateway** (e.g. `https://api.docnexus.ai` or `http://localhost:8010`) with header `X-API-Key: dnx_xxx`.
2. Kong **key-auth** plugin validates the key against its consumers (or a custom plugin calls the API Key Service `/api/v1/validate`).
3. If valid, Kong forwards the request to **docnexus-link** (upstream, e.g. `http://host.docker.internal:8000` locally).
4. docnexus-link serves the request (v1 or v5 routes). Optionally, a middleware or Kong plugin logs the request to the API Key Service `POST /api/v1/usage/log` (key_id, endpoint, status, latency).
5. Response is returned to the client.

**Path B — Direct to docnexus-link (local without Kong):**

1. Client sends a request to **docnexus-link** at `http://localhost:8000` with or without an API key.
2. docnexus-link v1 gateway routes do not require a key when called directly (key enforcement is at Kong in production). Response is returned.

### 4.4 Usage and limits

- **Stored**: In the API Key Service (per key: rate_limit_per_minute, rate_limit_per_month, concurrent_request_limit).
- **Enforced**: By Kong (rate-limiting plugin per consumer) or by a custom plugin that calls the API Key Service and enforces limits. The UI shows “of 500K limit” and usage so that limits are visible and not exceeded when enforcement is enabled.

---

## 5. Production deployment flow

### 5.1 Assumed topology

- **Frontend**: Hosted on CDN/Amplify; domain e.g. `https://app.docnexus.ai`. Uses Cognito for sign-in; env vars point to production API Key Service and (if needed) gateway.
- **API Key Service**: Behind a load balancer / API gateway; internal or public URL e.g. `https://api-keys.docnexus.ai`. Database: Postgres. CORS allows the frontend origin. Auth: validate Cognito JWT and derive user/org (no `X-User-Email` in prod).
- **Kong**: Public gateway at e.g. `https://api.docnexus.ai`. Kong has a DB (Postgres); consumers and key-auth credentials are created when keys are created (sync from API Key Service via Kong Admin API). Upstream is the internal URL of docnexus-link.
- **docnexus-link**: Internal service; Kong is the only public entry point for API traffic. Listens on an internal port; no direct exposure of docnexus-link to the internet if not required.

### 5.2 Production flow summary

1. **User** signs in (Cognito) → opens API Platform → frontend calls API Key Service with **JWT** (or token-derived identity). API Key Service validates JWT and resolves org.
2. **User** creates a key → API Key Service stores key and metadata → (optional) syncs **consumer + credential + rate limit** to Kong via Admin API.
3. **SDK/client** calls `https://api.docnexus.ai/v1/...` with `X-API-Key` → **Kong** validates key → forwards to **docnexus-link** → response returned; usage can be logged to the API Key Service.
4. **User** views Overview/Usage in the UI → frontend calls API Key Service (with JWT) → API Key Service returns usage for the user’s org.

### 5.3 Environment-specific base URLs

| Environment | Frontend        | API Key Service      | Gateway (Kong) / Backend |
|-------------|-----------------|----------------------|---------------------------|
| Local (no Kong) | http://localhost:3000 | http://localhost:8002 | http://localhost:8000 (docnexus-link) |
| Local (with Kong) | http://localhost:3000 | http://localhost:8002 | http://localhost:8010 (Kong) |
| Production | https://app.docnexus.ai | https://api-keys.docnexus.ai | https://api.docnexus.ai (Kong) |

SDK `baseUrl` must point to the **gateway** (Kong) in production, or directly to docnexus-link when Kong is not used.

---

## 6. Design decisions

| Decision | Rationale |
|----------|-----------|
| **Separate API Key Service** | Keeps key and usage logic out of docnexus-link; docnexus-link stays focused on search/profile. Same keys can be used by Kong and by other gateways or tools. |
| **Kong as gateway** | Industry-standard API gateway: key-auth, rate-limiting, routing, and (with DB) dynamic consumers. Offloads auth and limits from the backend. |
| **Local Kong on 8010/8011** | docnexus-link stays on 8000 so backend URLs are stable; Kong runs on 8010/8011 so all services can run locally without port collision. |
| **Two roles: admin and member** | Admin: full key lifecycle and endpoint permissions. Member: only edit which endpoints a key can access. Covers “key admins” vs “developers who tune permissions.” |
| **Key prefixes (dnx_prod_, dnx_dev_, dnx_test_)** | Visual distinction of environment; easy to restrict test keys to test backends in production. |
| **Bootstrap endpoint for first org admin** | Orgs are created without members; bootstrap adds the first admin so they can then invite others. Avoids chicken-and-egg (no member can call invite until someone exists). |
| **Validate endpoint on API Key Service** | Kong (or any gateway) can call `/api/v1/validate` with the incoming key and get 200 + rate-limit headers or 401. Allows central key storage with any gateway. |
| **Env-based Amplify config** | Cognito user pool and client can be set via `.env` (VITE_COGNITO_*) so the app runs without a committed `aws-exports` and works in CI/local with different pools. |
| **V1 gateway routes in docnexus-link** | `/v1/hcp-profiles/:npi` and `/v1/script-lift/analyze` live in the backend so Kong only routes; no path rewriting. Backend can add key validation later if needed. |
| **Usage log endpoint** | Kong or the backend can POST to the API Key Service to log each request (key_id, endpoint, status, latency) so the UI shows real usage without Kong plugins. |

---

## 7. Environment variables reference

### 7.1 API Key Service (`api-key-service/.env`)

| Variable | Default | Purpose |
|----------|---------|--------|
| `DATABASE_URL` | `sqlite:///./api_keys.db` | SQLite (dev) or Postgres URL (prod). |
| `KONG_ADMIN_URL` | — | Kong Admin API (e.g. `http://localhost:8011` local, `https://kong-admin.internal` prod). Used when syncing consumers. |
| `BACKEND_URL` | — | docnexus-link base URL (e.g. `http://localhost:8000`). |
| `JWT_SECRET_KEY` | — | For future JWT validation of frontend tokens. |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Allowed origins for the API Key Service. |

### 7.2 docnexus-frontend (`.env`)

| Variable | Purpose |
|----------|---------|
| `VITE_COGNITO_USER_POOL_ID` | Cognito user pool ID. |
| `VITE_COGNITO_CLIENT_ID` | Cognito app client ID. |
| `VITE_COGNITO_DOMAIN` | Cognito hosted UI domain (e.g. `xxx.auth.region.amazoncognito.com`). |
| `VITE_API_KEY_SERVICE_URL` | API Key Service base URL (default `http://localhost:8002`). |

### 7.3 docnexus-link

- Uses existing `.env` (DB, JWT, etc.). No API Platform–specific vars required for the v1 gateway routes.

### 7.4 Kong

- Configured via `kong.yml`. Upstream URL in that file (e.g. `http://host.docker.internal:8000` local) must match the actual docnexus-link URL.

---

## 8. Quick start (local)

Ports below are the **single source of truth** for local development.

1. **API Key Service** (port **8002**)
   ```bash
   cd api-key-service && ./run.sh
   ```

2. **docnexus-link** (port **8000**)
   ```bash
   cd docnexus-link && ./run.sh
   ```

3. **docnexus-frontend** (port **3000**)
   ```bash
   cd docnexus-frontend && npm run dev
   ```
   Set `.env` (Cognito, optional `VITE_API_KEY_SERVICE_URL=http://localhost:8002`). For API Platform, set `window.__API_PLATFORM_USER_EMAIL__` to an org member email (or bootstrap an org first).

4. **(Optional) Kong** (proxy **8010**, admin **8011**)
   ```bash
   cd kong && docker compose up -d
   ```
   Then use `http://localhost:8010` as the SDK `baseUrl` and send `X-API-Key` with a key that exists as a Kong consumer (or add the key to Kong).

5. **Bootstrap and create a key** (see [E2E_TESTING_GUIDE.md](./E2E_TESTING_GUIDE.md)):
   - `POST http://localhost:8002/api/v1/orgs` with optional `admin_email`
   - Or `POST http://localhost:8002/api/v1/orgs/1/bootstrap` with `{"admin_email":"you@example.com"}`
   - Then `POST http://localhost:8002/api/v1/keys` with `X-User-Email` and body `{"name":"My Key","environment":"testing"}`

---

## 9. Related docs

| Document | Contents |
|----------|----------|
| [E2E_TESTING_GUIDE.md](./E2E_TESTING_GUIDE.md) | Step-by-step curl, UI, and SDK testing; troubleshooting. |
| [API_PLATFORM_README.md](./API_PLATFORM_README.md) | High-level feature list and quick start. |
| [api-key-service/README.md](./api-key-service/README.md) | API Key Service endpoints and Kong integration. |
| [kong/README.md](./kong/README.md) | Kong run instructions and local ports (8010/8011). |
| [docnexus-sdk/README.md](./docnexus-sdk/README.md) | SDK install and usage; `baseUrl` for Kong vs direct link. |

---

**Summary**: Local ports are **8000** (link), **8002** (API Key Service), **3000** (frontend), **8010** (Kong proxy), **8011** (Kong admin). Production flow uses Cognito for users, API Key Service for keys and usage, Kong for gateway and rate limits, and docnexus-link as the backend behind Kong. All design choices above are documented for consistency and onboarding.
