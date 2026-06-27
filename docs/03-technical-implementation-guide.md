# Technical Implementation Guide — Inventra

This document is a build blueprint: it specifies, step by step, how the database,
backend service layer, REST API, MCP server, and frontend are constructed and wired
together. It is precise enough to regenerate the application. The data model and overall
architecture are defined in the Logical Structure Document; the verbatim MCP tool
contracts are in `MCP_TOOLS.md` (authoritative).

---

## 1. Technology stack

- **Backend:** Python, FastAPI, SQLAlchemy ORM, PostgreSQL
- **Auth:** JWT (bearer tokens), bcrypt password hashing
- **Agent interface:** MCP (Model Context Protocol) server over stdio, built on the
  `mcp` package (FastMCP), version pinned in `requirements.txt`
- **Email:** Resend (transaction receipts) — REST path only
- **Frontend:** React + TypeScript, single-page dashboard calling the REST API
- **Config:** environment variables via `.env` (`load_dotenv()`)

## 2. Project layout

```
app/
  main.py            FastAPI app; registers routers; creates tables on startup
  database.py        SQLAlchemy engine, SessionLocal, get_db generator dependency
  models.py          ORM models: User, Product, Transaction
  schemas.py         Pydantic request/response models
  auth.py            hash_password, verify_password, create_access_token, verify_token
  email.py           Resend email helpers (receipts, low-stock alerts)
  exceptions.py      ProductNotFoundError, InsufficientStockError(available, requested)
  services/
    products.py      lookup_stock(db, owner_id, product_id=None)
    transactions.py  record_transaction(db, owner_id, product_id, type, quantity, note)
    alerts.py        list_low_stock, list_expiring, get_dashboard_summary,
                     get_revenue_analytics
  routers/
    auth.py          /auth/register, /auth/login, get_current_user dependency
    products.py      /products CRUD
    transactions.py  /transactions (record + history)
    alerts.py        /alerts/* (low-stock, expiring, dashboard, revenue analytics)
  mcp_server.py      stdio MCP server exposing 6 tools over the service layer
tests/test_api.py
frontend/            minimal React/TS dashboard (Section 9)
```

## 3. Setup and run

1. Create a virtualenv and `pip install -r requirements.txt`.
2. Set environment variables in `.env`: database URL, JWT secret, Resend API key, and
   `INVENTRA_OWNER_EMAIL` (used by the MCP server — see Section 8).
3. **Run the REST API:** `uvicorn app.main:app --reload`. Tables are created on startup.
4. **Run the MCP server:** `python -m app.mcp_server`
   — **must** be launched as a module, never as `python app/mcp_server.py`. Running it
   as a bare script puts `app/` on `sys.path`, where the local `app/email.py` shadows
   the standard-library `email` package that `importlib.metadata` needs at import time,
   crashing with `ModuleNotFoundError: No module named 'email.errors'`. The `-m` form
   keeps `app/` off `sys.path` and avoids the shadow.

## 4. Database layer

- **Models** (`app/models.py`): `User`, `Product`, `Transaction` (full field list and
  relationships in the Logical Structure Document). `Product.sku` is unique;
  `Product.low_stock_threshold` defaults to 10; `Transaction.type` is an enum
  (`sale` | `restock`).
- **Table creation:** `Base.metadata.create_all(bind=engine)` runs on app startup in
  `main.py`.
- **Sessions — two regimes:**
  - **REST path:** `get_db()` is a generator dependency that yields a request-scoped
    session and closes it when the request ends (FastAPI manages the lifecycle).
  - **MCP path:** each tool opens its own session via `SessionLocal()` and closes it in
    a `finally` block (Section 8). FastAPI's dependency injection is not available here.
- **Tenant scoping:** every product/transaction query filters by `owner_id`.

## 5. Authentication (REST path)

- `POST /auth/register` — hashes the password with bcrypt (`hash_password`), persists
  the `User`.
- `POST /auth/login` — verifies credentials, returns a JWT access token
  (`create_access_token`).
- `get_current_user` — a FastAPI dependency that reads the `Authorization: Bearer
  <token>` header, decodes/validates the token (`verify_token`), and resolves the
  `User`. All product/transaction/alert routes depend on it.

The MCP path does **not** use JWT; it resolves a single owner at startup (Section 8).

## 6. Service layer (the shared core)

These plain functions are the single source of business logic. They take a SQLAlchemy
`Session` and an integer `owner_id` (never an ORM `User` object, never FastAPI types),
and raise **domain exceptions** rather than HTTP errors.

| Function | Signature | Behavior |
|---|---|---|
| `lookup_stock` | `(db, owner_id, product_id=None)` | `product_id=None` → all owner products; else the one product. Raises `ProductNotFoundError` if not found/owned. |
| `record_transaction` | `(db, owner_id, product_id, type, quantity, note)` | Validates `type` ∈ {sale, restock}. For a sale, if `quantity > product.quantity` raises `InsufficientStockError(available, requested)`; else deducts (sale) or adds (restock) stock and persists the `Transaction`. **Does not send email.** |
| `list_low_stock` | `(db, owner_id)` | Products where `quantity <= low_stock_threshold`. |
| `list_expiring` | `(db, owner_id, days=7)` | Products expiring within `days`. |
| `get_dashboard_summary` | `(db, owner_id)` | Counts: total products, low-stock, expiring-soon. |
| `get_revenue_analytics` | `(db, owner_id)` | Joins sales to products; daily revenue/cost/profit + summary totals and margin. |

**Error contract:** `ProductNotFoundError` and `InsufficientStockError(available,
requested)` are the only business errors. Each caller (REST router or MCP tool)
translates them into its own format.

## 7. REST API endpoints

Each endpoint requires a valid bearer token (`get_current_user`), calls the matching
service function with the authenticated user's id, and translates domain exceptions:
`ProductNotFoundError` → **404**, `InsufficientStockError` → **400**
(`"Not enough stock. Available: {n}"`).

| Method & path | Purpose | Service call |
|---|---|---|
| `POST /auth/register` | Create account | — |
| `POST /auth/login` | Get JWT | — |
| `GET /products/` | List products | `lookup_stock(db, owner_id)` |
| `GET /products/{product_id}` | One product | `lookup_stock(db, owner_id, product_id)` |
| `POST /products/` | Create product | (create) |
| `PUT /products/{product_id}` | Update product | (update) |
| `DELETE /products/{product_id}` | Delete product | (delete) |
| `POST /transactions/` | Record sale/restock | `record_transaction(...)` then send email receipt |
| `GET /transactions/` | Transaction history | (list) |
| `GET /alerts/low-stock` | Low-stock products | `list_low_stock(...)` |
| `GET /alerts/expiring` | Expiring products | `list_expiring(...)` |
| `GET /alerts/dashboard` | Dashboard counts | `get_dashboard_summary(...)` |
| `GET /alerts/analytics/revenue` | Revenue analytics | `get_revenue_analytics(...)` |

> These paths were verified against the live FastAPI app's OpenAPI schema; the
> create/update/delete shapes follow standard FastAPI + Pydantic CRUD conventions.

**Email side effect:** only `POST /transactions/` sends a Resend receipt, and it does so
in the router *after* the service call returns — never inside the service function.

## 8. MCP server (the agent interface)

`app/mcp_server.py` exposes the service layer as agent-callable tools.

- **Transport:** stdio.
- **Owner resolution at startup:** read `INVENTRA_OWNER_EMAIL`, look up that user, and
  cache their **`owner_id` (an integer)**. If the variable is unset or no user matches,
  raise a `RuntimeError` naming the problem so the server refuses to start in a broken
  state. Cache the integer id, not the ORM object (a cached object detaches once its
  session closes).
- **Per-call session + serialization rule:** each tool opens its own `SessionLocal()`,
  calls the matching service function with the cached `owner_id`, **serializes all
  results to plain JSON-safe dicts while the session is still open** (dates via
  `.isoformat()`, the transaction-type enum via `.value`, relationship fields like
  `product.name` read before close), then closes the session in `finally`. Returning ORM
  objects or reading lazy relationships after close raises `DetachedInstanceError`.
- **No email:** the MCP path never imports `app.email`.

### The six tools

Inputs and full output dicts are specified verbatim in `MCP_TOOLS.md`. Summary:

| Tool | Input | Wraps | Notable output |
|---|---|---|---|
| `lookup_stock` | `product_id?: int` (omit → list all) | `lookup_stock` | `{success, product(s)}`; `{success:false, error:"product_not_found", product_id}` |
| `record_transaction` | `product_id: int`, `type: "sale"\|"restock"`, `quantity: int`, `note?: str` | `record_transaction` | success: `{success, transaction{...updated qty...}}`; refusal: `{success:false, error:"insufficient_stock", available, requested, message}`; also `invalid_type`, `product_not_found` |
| `list_low_stock` | none | `list_low_stock` | `{success, products[]}` |
| `list_expiring` | `days?: int = 7` | `list_expiring` | `{success, products[]}` |
| `get_dashboard_summary` | none | `get_dashboard_summary` | `{success, total_products, low_stock_count, expiring_soon_count}` |
| `get_revenue_analytics` | none | `get_revenue_analytics` | `{success, daily[], summary{total_revenue, total_cost, total_profit, profit_margin}}` |

**Key design point:** the `record_transaction` refusal is a *structured* error
(`available` + `requested` as fields), so an agent can read why the sale was rejected
and retry with a valid quantity — not just receive an opaque string.

### Client configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "inventra": {
      "command": "<path-to-venv-python>",
      "args": ["-m", "app.mcp_server"],
      "cwd": "<repo-root>",
      "env": { "INVENTRA_OWNER_EMAIL": "owner@example.com" }
    }
  }
}
```

`cwd` must be the repo root so `-m app.mcp_server` resolves and `.env` discovery works.

## 9. Frontend — minimal reference dashboard

A single-page React + TypeScript app that demonstrates the human path against the REST
API. Deliberately minimal so it matches this spec closely.

- **Auth:** a login screen posts to `/auth/login`, stores the returned JWT in memory,
  and sends it as `Authorization: Bearer <token>` on every subsequent request.
- **Components / views (one page):**
  1. **Product list** — fetches `GET /products/`; table of name, sku, quantity, price.
  2. **Low-stock panel** — fetches `GET /alerts/low-stock`; highlights at-risk items.
  3. **Record-transaction form** — fields product, type (sale/restock), quantity, note;
     posts `POST /transactions/`; on a 400 insufficient-stock response, shows the error
     inline.
  4. **Revenue chart** — fetches `GET /alerts/analytics/revenue`; plots the `daily`
     series (revenue/profit) and shows the `summary` totals.
- **Data flow:** all reads/writes go through the REST API; no business logic lives in
  the frontend.

## 10. How it interconnects

The data layer is fronted by the service layer, which is the only code that holds
business rules. Two thin adapters sit on top: the REST routers (for the React dashboard,
authenticated by JWT, with the email side effect) and the MCP server (for an AI agent,
single-tenant, no email). Because both adapters call the identical service functions,
the oversell guard and every other rule behave the same regardless of who initiates the
action. See the Logical Structure Document for the architecture diagram and data-flow
narratives.