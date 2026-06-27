# Inventra — Agent-Operable Inventory & Sales Management API

A production-grade inventory and sales platform for small businesses. Built with FastAPI
and PostgreSQL, with automated stock tracking, email receipts via a custom domain,
scheduled daily alerts, and CI/CD. Its core business logic is operable **two ways**: by a
human through a REST API + React dashboard, and by an **AI agent** through a Model
Context Protocol (MCP) server — both backed by the same service layer, so the rules can
never drift between them.

🌐 **Live API Docs:** https://inventra-api-ernr.onrender.com/docs
💻 **Production Frontend (separate repo):** https://github.com/Khine12/inventra-frontend
🚀 **Live Demo:** https://inventra-frontend-alpha.vercel.app

---

## Project documentation

This repository includes a sample-project packet documenting the system precisely enough
to regenerate it from the text alone. Four components:

| Component | File |
|---|---|
| 1. Business Statement | [`docs/01-business-statement.md`](docs/01-business-statement.md) |
| 2. Logical Structure Document | [`docs/02-logical-structure.md`](docs/02-logical-structure.md) |
| 3. Technical Implementation Guide | [`docs/03-technical-implementation-guide.md`](docs/03-technical-implementation-guide.md) |
| 4. Application Code | `app/` (backend) · `frontend/` (reference dashboard) |
| Supporting: verified MCP tool contracts | [`docs/MCP_TOOLS.md`](docs/MCP_TOOLS.md) |

---

## Features

- **JWT Authentication** — secure register and login with bcrypt password hashing
- **Product Management** — full CRUD with SKU tracking, pricing, and configurable low-stock thresholds
- **Transaction Recording** — sales and restocks with automatic atomic stock deduction
- **Negative Stock Guard** — server-side validation prevents inventory going below zero (enforced in the service layer, so it holds for both the REST and MCP paths)
- **Agent Interface (MCP)** — an MCP server exposes the same operations as agent-callable tools, so an AI assistant can run inventory by conversation (see below)
- **Low-Stock Alerts** — endpoint automatically flags products below their threshold
- **Expiry Date Tracking** — alerts for products expiring within N days
- **Email Receipts** — Resend API fires a transaction confirmation email after every sale on the REST path, from custom domain `noreply@khinezarhein.com` (the MCP path is side-effect-isolated and sends no email)
- **Scheduled Daily Alerts** — APScheduler checks low-stock and expiring items every morning at 8AM and emails sellers automatically
- **Dashboard Summary** — total products, low-stock count, expiring-soon count in one endpoint
- **9 pytest tests** — covers auth flow, product CRUD, negative stock guard, alert endpoints
- **CI/CD** — GitHub Actions runs the full test suite on every push to main

---

## Agent interface (MCP)

`app/mcp_server.py` is a stdio MCP server that re-exposes the existing service layer as
six agent-callable tools, so an AI agent (e.g. Claude Code or Claude Desktop) can operate
the inventory directly — *"sold 5 units of SKU-203, log it and flag anything low"* — and
the agent calls the tools, respects the same oversell guard, and reports back.

| Tool | Purpose |
|---|---|
| `lookup_stock` | One product by id, or list all |
| `record_transaction` | Record a sale/restock (oversell-guarded) |
| `list_low_stock` | Products at/under threshold |
| `list_expiring` | Products expiring within N days |
| `get_dashboard_summary` | Total / low-stock / expiring counts |
| `get_revenue_analytics` | Daily revenue/cost/profit + summary |

Design points: the server resolves a single owner at startup
(`INVENTRA_OWNER_EMAIL`), owns its own DB session per call, and returns a **structured**
error on an oversell (`{error: "insufficient_stock", available, requested}`) so an agent
can reason about the refusal and retry. Full, verified tool contracts (exact input
schemas and output shapes) are in [`docs/MCP_TOOLS.md`](docs/MCP_TOOLS.md).

**Run it** (launch as a module — never as a bare script — to avoid `app/email.py`
shadowing the stdlib `email` package):

```bash
INVENTRA_OWNER_EMAIL=owner@example.com python -m app.mcp_server
```

To connect it to an agent, point an MCP client at that command. With Claude Code, from
the repo root:

```bash
claude mcp add inventra -e INVENTRA_OWNER_EMAIL=owner@example.com -- <venv-python> -m app.mcp_server
```

---

## Connect to Claude Code

The command above registers the server, but two things have to be right before
`claude mcp get inventra` reports `Status: ✓ Connected`:

```bash
claude mcp add inventra -e INVENTRA_OWNER_EMAIL=<real-seeded-email> -- <venv-python> -m app.mcp_server
```

> **Gotcha 1 — cwd:** `claude mcp add` has no `--cwd` flag, but `python -m app.mcp_server`
> only resolves the `app` package when launched from the repo root. Without it, Claude
> Code spawns the process from its own working directory and the server fails with
> `ModuleNotFoundError: No module named 'app'`. Fix it by adding `"cwd": "<repo-root>"`
> directly to the `inventra` entry in `~/.claude.json` — the field isn't exposed by the
> `add` CLI, but the runtime honors it.
>
> **Gotcha 2 — owner email:** `INVENTRA_OWNER_EMAIL` must be a real, already-registered
> Inventra account, not the `owner@example.com` placeholder. The server resolves this
> user at startup and intentionally raises an error rather than starting in a broken
> state if no matching account exists.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL (Neon) |
| ORM | SQLAlchemy |
| Auth | JWT (python-jose, bcrypt) |
| Agent interface | MCP (Model Context Protocol), stdio transport |
| Email | Resend API |
| Scheduling | APScheduler |
| Frontend | React + TypeScript + Vite (reference dashboard) |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Deployment | Render |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new business account |
| POST | `/auth/login` | Login and receive JWT token |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List all products for authenticated user |
| POST | `/products/` | Create a new product |
| GET | `/products/{product_id}` | Get a single product |
| PUT | `/products/{product_id}` | Update product details |
| DELETE | `/products/{product_id}` | Delete a product |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transactions/` | Record a sale or restock — auto-updates stock |
| GET | `/transactions/` | Get all transactions |
| GET | `/transactions/product/{id}` | Get transaction history for a product |

### Alerts & Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts/low-stock` | Products at or below their threshold |
| GET | `/alerts/expiring?days=7` | Products expiring within N days |
| GET | `/alerts/dashboard` | Summary: total products, low stock, expiring counts |

---

## Architecture

A single service layer holds all business logic and is the only code that touches the
database. Two thin adapters sit on top: the **REST API** (for the React dashboard,
authenticated by JWT, with the email side effect) and the **MCP server** (for an AI
agent, single-tenant, no email). Because both call the identical service functions, the
oversell guard and every other rule behave the same regardless of who initiates the
action. The full architecture diagram and data-flow narratives are in
[`docs/02-logical-structure.md`](docs/02-logical-structure.md).

```
   React Dashboard (human)          AI Agent (MCP client)
            │ HTTP + JWT                     │ tool calls
            ▼                                ▼
     FastAPI REST routers            MCP server (stdio)
            └──────────────┬─────────────────┘
                           ▼
                    Service layer  ──►  PostgreSQL (Neon)
                           │
        REST path only ──► Resend email · APScheduler 8AM alerts
```

---

## Repository structure

```
app/          FastAPI backend: models, service layer, REST routers, MCP server
frontend/     Minimal React + TypeScript reference dashboard (human path)
docs/         The four submission documents
tests/        pytest suite
```

> **Submission scope:** this repository is self-contained — backend, a minimal reference
> dashboard matching the implementation guide, and the docs. A fuller production frontend
> is deployed separately (linked above) from `Khine12/inventra-frontend`.

---

## Local Development

```bash
# Clone the repo
git clone https://github.com/Khine12/inventra.git
cd inventra

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your values

# Run the REST API
uvicorn app.main:app --reload

# Run the reference frontend (separate terminal)
cd frontend && npm install && npm run dev    # http://localhost:5173

# Run the MCP server (separate terminal)
INVENTRA_OWNER_EMAIL=owner@example.com python -m app.mcp_server

# Run tests
pytest tests/ -v
```

---

## Environment Variables

```
DATABASE_URL=your_neon_postgresql_connection_string
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RESEND_API_KEY=your_resend_api_key
INVENTRA_OWNER_EMAIL=owner@example.com   # used by the MCP server to resolve the owner
```

---

## CI/CD

GitHub Actions automatically runs the full pytest suite on every push to `main`. All 9
tests must pass before deployment.