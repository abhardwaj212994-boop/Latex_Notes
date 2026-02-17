# Kong + API key + mTLS flow

Flowcharts for how the **whole API-key project** works: where the code lives, production vs local, request flow, and before/after Kong.

---

## Where the frontend and API-key code lives

The API-key project spans **four repos**. Frontend and backend that manage keys, plus the three backends behind Kong.

```mermaid
flowchart TB
    subgraph docnexus_frontend["docnexus-frontend (React/Vite)"]
        ApiKeys["ApiKeys.tsx<br/>List / create / delete API keys"]
        Docs["Documentation.tsx<br/>DocNexus client example, DOCNEXUS_API_KEY"]
        Service["apiPlatformService.ts<br/>Calls API Platform backend (JWT)"]
        Env1["VITE_APP_API_PLATFORM_URL /<br/>REACT_APP_API_PLATFORM_URL"]
        ApiKeys --> Service
        Docs --> Env1
    end

    subgraph docnexus_api_platform["docnexus-api-platform (FastAPI)"]
        KeysRouter["routers/keys.py<br/>GET/POST/DELETE /api/v1/keys"]
        KongService["services/kong_service.py<br/>Kong Admin / Konnect: consumers, key-auth"]
        DynamoDB["services/dynamodb_service.py<br/>kong_consumer_id, dashboard"]
        KeysRouter --> KongService
        KongService --> DynamoDB
    end

    subgraph backends["Backends (behind Kong)"]
        Link["docnexus-link<br/>kong/ + app :8080"]
        Adv["advanced-search<br/>kong/ + Next.js :3000"]
        Script["script-lift-app<br/>kong/ + Vite :8080"]
    end

    Service -->|"Bearer JWT"| KeysRouter
    KongService -->|"Create consumer + key"| KongCloud["Kong Konnect API"]
```

| Repo | Role | Key files for API keys / Kong |
|------|------|-------------------------------|
| **docnexus-frontend** | Dashboard UI: manage keys, docs | `src/pages/Dashboard/ApiPlatform/ApiKeys.tsx`, `Documentation.tsx`, `src/services/apiPlatformService.ts`; env: `VITE_APP_API_PLATFORM_URL` or `REACT_APP_API_PLATFORM_URL` |
| **docnexus-api-platform** | Backend: create/list/delete keys in Kong, store consumer id | `app/routers/keys.py`, `app/services/kong_service.py`, `app/services/dynamodb_service.py`; env: `API_PLATFORM_KONG_ADMIN_URL`, `API_PLATFORM_KONG_KONNECT_REALM_ID`, etc. |
| **docnexus-link** | Backend API | `kong/` (mTLS proxy, certs, README); route `/docnexus-link` → :8080 |
| **advanced-search** | Backend API | `kong/`; route `/advanced-search` → :3000 |
| **script-lift-app** | Backend API | `kong/`; route `/script-lift-app` → :8080 |

**API key creation flow (user creates a key in the dashboard):**

1. User is logged in to **docnexus-frontend** (Cognito).
2. User opens **API Platform → Keys** and clicks “Create key” (name, optional endpoints: script-lift, hcp-profiles, advanced-search).
3. **apiPlatformService** calls **docnexus-api-platform** `POST /api/v1/keys` with `Authorization: Bearer <Cognito id_token>`.
4. **docnexus-api-platform** ensures a Kong **Consumer** for that user (Konnect realm API or Kong Admin), then creates a **key-auth credential** for that consumer; stores `kong_consumer_id` in DynamoDB.
5. The new key value is returned **once** to the frontend and shown to the user (copy and use in `DOCNEXUS_API_KEY` or `apikey` header when calling the Kong Proxy URL).

---

## Production architecture (no local / no ngrok)

In production, Kong Konnect Data Plane runs in the cloud; backends are deployed on your infrastructure; no ngrok or localhost.

```mermaid
flowchart LR
    subgraph Clients["Clients"]
        App[External app / SDK]
        Browser[DocNexus dashboard]
    end

    subgraph Kong["Kong Konnect (cloud)"]
        Proxy["Proxy URL<br/>e.g. https://xxx.kongcloud.dev"]
        DP[Data Plane]
        CP[Control Plane<br/>config + keys]
        Proxy --> DP
        DP --> CP
    end

    subgraph YourInfra["Your infrastructure (VPC / cloud)"]
        Link["docnexus-link<br/>e.g. https://link.docnexus.ai"]
        Adv["advanced-search<br/>e.g. https://search.docnexus.ai"]
        Script["script-lift-app<br/>e.g. https://scriptlift.docnexus.ai"]
    end

    subgraph ApiPlatform["API Platform (key management)"]
        Frontend["docnexus-frontend<br/>Dashboard"]
        Backend["docnexus-api-platform<br/>Keys API"]
        Frontend --> Backend
        Backend -->|"Kong Admin / Konnect API"| CP
    end

    App -->|"GET /docnexus-link/...<br/>apikey: KEY"| Proxy
    DP -->|"Route by path"| Link
    DP --> Adv
    DP --> Script
    Browser --> Frontend
```

**Production request flow (API call with key):**

1. **Client** (external app or script) sends a request to **Kong Proxy URL**, e.g. `https://xxx.kongcloud.dev/docnexus-link/v5/search`, with header `apikey: <KEY>` or query `?apikey=<KEY>`.
2. **Kong Data Plane** (cloud) receives the request, matches **Route** (e.g. `/docnexus-link`), runs **key-auth**: validates the key against Konnect (Control Plane). If invalid or missing → **401 Unauthorized**.
3. If valid, Kong forwards to the **Service** upstream URL (production URL of the backend, e.g. `https://link.docnexus.ai`). Path is stripped per route config (e.g. `/docnexus-link/health` → upstream `/health`).
4. **Backend** (docnexus-link, advanced-search, or script-lift-app) receives the request **without** the API key (Kong does not forward it). Backend responds.
5. Response goes back: Backend → Kong → Client.

**Production optional mTLS:** If the Service URL in Kong is **HTTPS** and a **client certificate** is attached to the service, Kong sends that certificate when calling the backend. The backend (or an mTLS proxy in front of it) must then verify the client cert. In production the mTLS proxy (or TLS termination) would run on your servers, not locally.

```mermaid
flowchart TB
    subgraph Production["Production (simplified)"]
        C[Client]
        K[Kong Konnect<br/>Proxy URL]
        S1[docnexus-link<br/>production URL]
        S2[advanced-search<br/>production URL]
        S3[script-lift-app<br/>production URL]
        C -->|"apikey"| K
        K -->|"Valid key → forward"| S1
        K --> S2
        K --> S3
    end
```

No ngrok, no localhost: Kong and backends use real hostnames and (optionally) private networking or public HTTPS.

---

## Request flow with mTLS enabled

When mTLS is turned on, Kong presents a **client certificate** when calling the backend; the backend (or an mTLS proxy in front of it) **verifies** that cert. Only Kong (holding that cert) can complete the TLS handshake and reach the app.

```mermaid
flowchart LR
    subgraph Client["Client"]
        Req["Request<br/>apikey: KEY"]
    end

    subgraph Kong["Kong Konnect"]
        Proxy[Proxy]
        Auth[Validate API key]
        Fwd[Forward to Service URL]
        Cert[Attach client cert<br/>kong-client.crt/key]
        Proxy --> Auth
        Auth -->|"Valid"| Fwd
        Fwd --> Cert
    end

    subgraph Backend["Your infrastructure"]
        TLS["TLS handshake<br/>Server: server.crt<br/>Client: must present cert"]
        Verify["Verify client cert<br/>against CA (ca.crt)"]
        Proxy8443["mTLS proxy :8443"]
        App["App :8080"]
        TLS --> Verify
        Verify -->|"Cert valid"| Proxy8443
        Proxy8443 --> App
    end

    Req --> Proxy
    Cert -->|"HTTPS + client cert"| TLS
    App --> Response["Response"]
    Response --> Client
```

**Step-by-step (mTLS enabled):**

```mermaid
flowchart TB
    subgraph Steps["Request path with mTLS"]
        S1["1. Client → Kong Proxy URL with apikey header"]
        S2["2. Kong validates API key → 401 if invalid"]
        S3["3. Kong looks up Service: URL = https://... (HTTPS)"]
        S4["4. Kong attaches client certificate (kong-client.crt + key) to outbound TLS"]
        S5["5. Kong opens TLS connection to upstream (e.g. mTLS proxy :8443)"]
        S6["6. mTLS proxy receives TLS ClientHello + client cert"]
        S7["7. Proxy verifies client cert with CA (ca.crt)"]
        S8["8. If cert invalid or missing → 403 / close connection"]
        S9["9. If cert valid → proxy forwards request to app (HTTP :8080)"]
        S10["10. App responds → proxy → Kong → Client"]
    end

    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7
    S7 --> S8
    S7 --> S9 --> S10
```

**What lives where (mTLS enabled):**

| Component | Role |
|-----------|------|
| **Kong (Control Plane)** | Stores **kong-client.crt** + **kong-client.key** as a Certificate entity; attached to the Service so the Data Plane uses them when calling the HTTPS upstream. |
| **Kong Data Plane** | Validates API key, then connects to Service URL over **HTTPS** and presents the client cert during TLS handshake. |
| **mTLS proxy (your server)** | Listens on **HTTPS** (:8443); uses **server.crt** + **server.key**; verifies client cert with **ca.crt**. Rejects (403) if no cert or cert not signed by CA. Proxies to app over HTTP. |
| **App (docnexus-link, etc.)** | Listens on HTTP (:8080); no TLS, no certs. Only reachable from the mTLS proxy (or directly if someone has network access). |

So with mTLS enabled: **only Kong** (with the client cert) can successfully call the mTLS proxy; direct calls to :8443 without a valid client cert get 403.

---

## Local / testing flow (Kong + optional ngrok + mTLS)

*Below is the **local development** setup: backends on localhost, optional ngrok for Konnect, optional mTLS proxy.*

## 1. Full request flow (API key + Kong + optional mTLS) — local

End-to-end path when a client calls the API through Kong Konnect with an API key. Option A = HTTP upstream (no mTLS); Option B = HTTPS upstream with mTLS.

```mermaid
flowchart LR
    subgraph Client
        C[Client app]
    end

    subgraph Kong["Kong Konnect"]
        DP[Data Plane]
        CP[Control Plane]
        DP --> CP
    end

    subgraph Tunnel["Tunnel (Konnect only)"]
        N[ngrok]
    end

    subgraph OptionA["Option A: HTTP upstream"]
        A_App[docnexus-link :8080]
    end

    subgraph OptionB["Option B: mTLS upstream"]
        Proxy[mTLS proxy :8443]
        B_App[docnexus-link :8080]
        Proxy --> B_App
    end

    C -->|"1. GET /docnexus-link/health<br/>apikey: YOUR_KEY"| DP
    DP -->|"2. Validate API key"| CP
    CP -->|"3. Key valid"| DP
    DP -->|"4a. HTTP to ngrok"| N
    N -->|"5a. Forward"| A_App
    DP -.->|"4b. HTTPS + client cert"| N
    N -.->|"5b. TCP forward"| Proxy
    A_App -->|"6. Response"| C
    B_App -->|"6. Response"| Proxy
    Proxy --> N
    N --> DP
    DP --> C
```

**Step-by-step (same flow, vertical):**

```mermaid
flowchart TB
    subgraph Steps["Request path"]
        S1["1. Client sends request to Kong Proxy URL<br/>(e.g. https://xxx.kongcloud.dev/docnexus-link/health)<br/>Header: apikey: &lt;API_KEY&gt; or ?apikey=..."]
        S2["2. Kong Data Plane receives request"]
        S3["3. Kong validates API key (key-auth / Konnect)"]
        S4["4. If invalid → 401 Unauthorized"]
        S5["5. If valid → Kong forwards to Service URL"]
    end

    subgraph OptionA["Option A – HTTP upstream (no mTLS)"]
        A1["6a. Kong → ngrok (HTTP)"]
        A2["7a. ngrok → localhost:8080"]
        A3["8a. docnexus-link responds"]
    end

    subgraph OptionB["Option B – mTLS upstream"]
        B1["6b. Kong → ngrok TCP (HTTPS + client cert)"]
        B2["7b. ngrok → localhost:8443 (raw TCP)"]
        B3["8b. mTLS proxy verifies client cert"]
        B4["9b. Proxy → localhost:8080 (HTTP)"]
        B5["10b. docnexus-link responds"]
    end

    S1 --> S2 --> S3
    S3 --> S4
    S3 --> S5
    S5 --> A1
    S5 --> B1
    A1 --> A2 --> A3
    B1 --> B2 --> B3 --> B4 --> B5
```

---

## 2. API key flow (where the key is checked)

Where the API key is validated and how it affects the request.

```mermaid
flowchart LR
    subgraph Client["Client"]
        Req["Request + apikey header/query"]
    end

    subgraph Kong["Kong Konnect"]
        Route[Route match]
        KeyAuth[Key Auth plugin]
        Service[Service / upstream]
        Route --> KeyAuth
        KeyAuth -->|"Valid key"| Service
        KeyAuth -->|"Missing/invalid"| 401[401 Unauthorized]
    end

    subgraph Backend["Your backend"]
        App[docnexus-link / advanced-search / script-lift-app]
    end

    Req --> Route
    Service -->|"Forward (no apikey to backend)"| App
    App --> Response["Response"]
    Response --> Client
    401 --> Client
```

- **API key is only checked at Kong.** The backend (docnexus-link, etc.) does not see or validate the API key; Kong strips or does not forward it depending on config.
- Keys are created and stored in Kong Konnect (Control Plane). The Data Plane validates them before forwarding.

---

## 3. Before vs after Kong

**Before:** Clients call the backend directly. No central auth, no gateway.

**After:** All traffic goes through Kong. API key (and optionally mTLS) at the gateway.

```mermaid
flowchart TB
    subgraph Before["BEFORE (no Kong)"]
        direction TB
        C1[Client 1]
        C2[Client 2]
        C3[Client 3]
        BE[Backend<br/>docnexus-link :8080]
        C1 --> BE
        C2 --> BE
        C3 --> BE
        Note1["No API key check<br/>No central auth<br/>Backend exposed directly"]
    end

    subgraph After["AFTER (with Kong)"]
        direction TB
        C4[Client 1]
        C5[Client 2]
        C6[Client 3]
        Kong[Kong Konnect<br/>Proxy URL]
        BE2[Backend<br/>docnexus-link :8080]
        C4 -->|"apikey"| Kong
        C5 -->|"apikey"| Kong
        C6 -->|"apikey"| Kong
        Kong -->|"Validate key → forward"| BE2
        Note2["API key required<br/>Optional mTLS to backend<br/>Single entry point"]
    end
```

---

## 4. Before vs after (single-request view)

```mermaid
flowchart LR
    subgraph Before["BEFORE"]
        A[Client] -->|"Direct HTTP"| B[Backend :8080]
    end

    subgraph After["AFTER"]
        C[Client] -->|"HTTPS + apikey"| D[Kong]
        D -->|"HTTP or HTTPS+mTLS"| E[Backend]
    end
```

| | Before | After |
|---|--------|--------|
| **URL** | `http://backend:8080/health` | `https://&lt;proxy&gt;/docnexus-link/health` |
| **Auth** | None (or app-specific) | API key (header or query) validated by Kong |
| **Backend reachable** | By anyone who can reach :8080 | Only via Kong (optional: only Kong can reach via mTLS on 8443) |

---

## 5. Components summary

```mermaid
flowchart TB
    subgraph External["External"]
        Client[Client]
    end

    subgraph KongKonnect["Kong Konnect (cloud)"]
        Proxy[Proxy URL]
        KeyAuth[API key validation]
        Proxy --> KeyAuth
    end

    subgraph YourSetup["Your setup (e.g. local dev)"]
        Ngrok[ngrok tunnel]
        MTLS[mTLS proxy :8443]
        App[App :8080]
        Ngrok --> MTLS
        MTLS --> App
    end

    Client -->|"apikey"| Proxy
    KeyAuth -->|"Forward"| Ngrok
```

- **API key:** Checked only at Kong; backend does not see it.
- **mTLS:** Used only between Kong and your mTLS proxy (Option B); only Kong holds the client cert, so only Kong can call the backend via 8443.

---

## Summary table: production vs local

| Aspect | Production | Local / testing |
|--------|------------|------------------|
| **Kong** | Konnect Data Plane in cloud; Proxy URL e.g. `https://xxx.kongcloud.dev` | Same Konnect, or Kong running locally (e.g. Docker) |
| **Backends** | Deployed (e.g. ECS, K8s, Lambda); URLs like `https://link.docnexus.ai` | `localhost:8080`, `:3000`, `:8080`; optional **ngrok** to expose for Konnect |
| **mTLS** | Optional: Kong → HTTPS + client cert to your backend (or mTLS proxy in front of backend) | Optional: Kong → ngrok **TCP** → mTLS proxy :8443 → app |
| **Key management** | Same: docnexus-frontend (Dashboard) → docnexus-api-platform → Kong Konnect API | Same |
| **Frontend** | docnexus-frontend deployed; users open Dashboard → API Platform → Keys | Same app, often `localhost`; env `VITE_APP_API_PLATFORM_URL` points to api-platform backend |
