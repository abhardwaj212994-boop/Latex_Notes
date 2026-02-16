# API Platform — Step-by-step flow diagram

This doc shows what happens at each step from sign-in to listing/creating/editing API keys.

---

## 1. High-level: who talks to whom

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Browser (User logged in via Cognito)                                        │
│  · React app (docnexus-frontend)                                             │
│  · Amplify holds: id token, access token                                     │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │  VITE_APP_KONG_API_URL (e.g. http://localhost:8000)
                                │  Every api-platform request: Authorization: Bearer <id token>
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  API Platform Backend (FastAPI, e.g. :8000)                                  │
│  · Verifies Cognito id token (if COGNITO_USER_POOL_ID set) → gets "sub"      │
│  · Scopes keys by sub: list/create/update only for that user                  │
│  · Calls Kong Admin API for consumers, key-auth, ACLs                         │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │  KONG_ADMIN_URL + KONG_ADMIN_TOKEN
                                │  (Kong Konnect Control Plane — core-entities)
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Kong Konnect                                                                 │
│  · Consumers (one per API key; custom_id = user "sub" for scoping)            │
│  · Key-auth credentials per consumer                                           │
│  · ACL groups per consumer (which routes/endpoints the key can call)         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Sign-in and token (before any API Platform call)

```
  User                Frontend (Amplify)           Cognito
   │                          │                       │
   │  Click Login              │                       │
   │ ────────────────────────>│                       │
   │                          │  Redirect / OAuth      │
   │                          │ ─────────────────────>│
   │                          │                       │
   │                          │  id token + access    │
   │                          │ <─────────────────────│
   │  Logged in                │  (stored in session)  │
   │ <────────────────────────│                       │
   │                          │                       │
   │  Later: fetchAuthSession() returns tokens        │
   │  idToken used for API Platform backend           │
```

- **Step 1:** User signs in via Cognito (Amplify).
- **Step 2:** Cognito returns **id token** (and access token). Frontend keeps them in session.
- **Step 3:** When the user opens API Platform and the app calls the backend, the frontend gets `idToken` from `fetchAuthSession()` and sends it as `Authorization: Bearer <id token>`.

---

## 3. List keys (GET /api-platform/keys)

```
  User     Frontend (API Platform)    Backend (FastAPI)           Kong Konnect
   │                │                        │                          │
   │  Open API Keys  │                        │                          │
   │ ──────────────>│                        │                          │
   │                │  GET /api-platform/keys                           │
   │                │  Authorization: Bearer <id token>                  │
   │                │ ───────────────────────>│                          │
   │                │                        │  (1) Verify JWT           │
   │                │                        │      → sub = "user-123"   │
   │                │                        │  (2) GET .../consumers   │
   │                │                        │ ─────────────────────────>│
   │                │                        │  list of all consumers   │
   │                │                        │ <─────────────────────────│
   │                │                        │  (3) Filter: custom_id  │
   │                │                        │      == "user-123"        │
   │                │                        │  (4) For each consumer:   │
   │                │                        │      GET .../key-auth,    │
   │                │                        │      GET .../acls         │
   │                │                        │ ─────────────────────────>│
   │                │                        │ <─────────────────────────│
   │                │  { keys: [...], stats }│                          │
   │                │ <──────────────────────│                          │
   │  See only      │                        │                          │
   │  my keys       │                        │                          │
   │ <──────────────│                        │                          │
```

**Steps in words:**

1. User clicks **API Keys** in the API Platform sidebar.
2. Frontend calls `GET /api-platform/keys` with `Authorization: Bearer <id token>`.
3. Backend reads the header and, if Cognito is configured, **verifies the JWT** with Cognito’s JWKS and reads **sub** (e.g. `"user-123"`).
4. Backend calls Kong: **GET .../consumers** and gets all consumers.
5. Backend **filters** consumers where **custom_id == sub** (only this user’s keys).
6. For each of those consumers, backend asks Kong for key-auth (masked) and ACLs, and builds the list.
7. Backend returns **{ keys, stats }** to the frontend.
8. User sees only their keys.

---

## 4. Create key (POST /api-platform/keys)

```
  User     Frontend                  Backend                         Kong
   │           │                         │                              │
   │  Create   │                         │                              │
   │  Key form │                         │                              │
   │  (name,   │                         │                              │
   │   endpoints,                       │                              │
   │   rate limit)                      │                              │
   │ ─────────>│                         │                              │
   │           │  POST /api-platform/keys                              │
   │           │  Authorization: Bearer <id token>                      │
   │           │  Body: { name, endpoints, rate_limit_per_minute }        │
   │           │ ──────────────────────>│                              │
   │           │                         │  (1) Verify JWT → sub        │
   │           │                         │  (2) POST .../consumers      │
   │           │                         │      body: { username,       │
   │           │                         │              custom_id: sub }│
   │           │                         │ ─────────────────────────────>│
   │           │                         │  consumer { id }             │
   │           │                         │ <─────────────────────────────│
   │           │                         │  (3) POST .../consumers/{id}/key-auth
   │           │                         │ ─────────────────────────────>│
   │           │                         │  { key }                      │
   │           │                         │ <─────────────────────────────│
   │           │                         │  (4) For each endpoint:       │
   │           │                         │      POST .../consumers/{id}/acls
   │           │                         │      body: { group: "access-*" }
   │           │                         │ ─────────────────────────────>│
   │           │                         │ <─────────────────────────────│
   │           │  { key, keyPreview,     │                              │
   │           │    consumer_id, ... }   │                              │
   │           │ <──────────────────────│                              │
   │  Copy key  │                         │                              │
   │  once      │                         │                              │
   │ <──────────│                         │                              │
```

**Steps in words:**

1. User fills the Create Key form (name, endpoints, rate limit) and submits.
2. Frontend sends **POST /api-platform/keys** with **Bearer id token** and the body.
3. Backend **verifies JWT** and gets **sub**.
4. Backend creates a **Kong consumer**: **POST .../consumers** with `username` (unique) and **custom_id = sub** so the key is tied to this user.
5. Backend creates the **key-auth** credential: **POST .../consumers/{id}/key-auth**. Kong returns the **key** (shown once).
6. Backend **adds ACL groups** for each chosen endpoint: **POST .../consumers/{id}/acls** with `group` = e.g. `access-script-lift`, `access-hcp-profiles`.
7. Backend returns **key**, **keyPreview**, **consumer_id**, **allowed_endpoints** to the frontend.
8. User copies the key (it’s only shown once).

---

## 5. Update key endpoints (PATCH /api-platform/keys/{consumer_id}/endpoints)

```
  User     Frontend                  Backend                         Kong
   │           │                         │                              │
   │  Edit     │                         │                              │
   │  endpoints│                         │                              │
   │  (add/    │                         │                              │
   │   remove) │                         │                              │
   │ ─────────>│                         │                              │
   │           │  PATCH .../keys/{consumer_id}/endpoints                 │
   │           │  Authorization: Bearer <id token>                       │
   │           │  Body: { add: [...], remove: [...] }                    │
   │           │ ──────────────────────>│                              │
   │           │                         │  (1) Verify JWT → sub         │
   │           │                         │  (2) GET .../consumers/{id}  │
   │           │                         │ ─────────────────────────────>│
   │           │                         │  consumer { custom_id }      │
   │           │                         │ <─────────────────────────────│
   │           │                         │  (3) If custom_id != sub      │
   │           │                         │      → 403 Forbidden          │
   │           │                         │  (4) GET .../consumers/{id}/acls
   │           │                         │ ─────────────────────────────>│
   │           │                         │  (5) POST acls for "add",     │
   │           │                         │      DELETE acls for "remove" │
   │           │                         │ ─────────────────────────────>│
   │           │  { ok: true }           │                              │
   │           │ <──────────────────────│                              │
   │  See       │                         │                              │
   │  updated   │                         │                              │
   │  list      │                         │                              │
   │ <──────────│                         │                              │
```

**Steps in words:**

1. User clicks “Edit endpoints” for a key and adds/removes endpoint checkboxes, then saves.
2. Frontend sends **PATCH .../keys/{consumer_id}/endpoints** with **Bearer id token** and **{ add, remove }**.
3. Backend **verifies JWT** and gets **sub**.
4. Backend **fetches that consumer** from Kong: **GET .../consumers/{consumer_id}**.
5. Backend **checks** that **consumer.custom_id == sub**. If not → **403 Forbidden** (can’t edit another user’s key).
6. Backend **GET .../consumers/{id}/acls**, then **POST** new ACL groups for `add` and **DELETE** ACLs for `remove`.
7. Backend returns **{ ok: true }**. Frontend can refetch the keys list so the user sees updated endpoints.

---

## 6. Summary table

| Step | Where | What happens |
|------|--------|----------------|
| 1 | Browser | User signs in with Cognito; Amplify stores id token. |
| 2 | Frontend | On API Platform requests, frontend sends `Authorization: Bearer <id token>`. |
| 3 | Backend | Verifies JWT with Cognito JWKS; reads **sub** (user id). |
| 4 | Backend | **List keys:** Kong list consumers → filter by **custom_id == sub** → return only that user’s keys. |
| 5 | Backend | **Create key:** Create Kong consumer with **custom_id = sub**, then key-auth + ACLs. |
| 6 | Backend | **Update endpoints:** Check consumer **custom_id == sub** → then add/remove ACLs in Kong. |
| 7 | Kong | Stores consumers, key-auth credentials, and ACL groups; enforces access on API routes. |

---

## 7. When Cognito is not configured

If the backend **does not** have `COGNITO_USER_POOL_ID` set:

- **No JWT check:** Backend does not require or read `Authorization`.
- **No scoping:** List keys returns **all** consumers from Kong; create key uses a unique `custom_id` (e.g. key name); update endpoints is not restricted by user.
- So the same backend can run in “single-tenant / no auth” mode (no Cognito) or “per-user keys” mode (Cognito set).
