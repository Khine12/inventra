# Inventra — Inventory & Sales Management API

A production-grade REST API for small business inventory management. Built with FastAPI and PostgreSQL, featuring automated stock tracking, email receipts via custom domain, scheduled daily alerts, and CI/CD with GitHub Actions.

🌐 **Live API Docs:** https://inventra-api-ernr.onrender.com/docs  
💻 **Frontend:** https://github.com/Khine12/inventra-frontend  
🚀 **Live Demo:** https://inventra-frontend-alpha.vercel.app

---

## Features

- **JWT Authentication** — secure register and login with bcrypt password hashing
- **Product Management** — full CRUD with SKU tracking, pricing, and configurable low-stock thresholds
- **Transaction Recording** — sales and restocks with automatic atomic stock deduction
- **Negative Stock Guard** — server-side validation prevents inventory going below zero
- **Low-Stock Alerts** — endpoint automatically flags products below their threshold
- **Expiry Date Tracking** — alerts for products expiring within N days
- **Email Receipts** — Resend API fires transaction confirmation emails automatically after every sale from custom domain `noreply@khinezarhein.com`
- **Scheduled Daily Alerts** — APScheduler checks low-stock and expiring items every morning at 8AM and emails sellers automatically
- **Dashboard Summary** — total products, low-stock count, expiring-soon count in one endpoint
- **9 pytest tests** — covers auth flow, product CRUD, negative stock guard, alert endpoints
- **CI/CD** — GitHub Actions runs full test suite on every push to main

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL (Neon) |
| ORM | SQLAlchemy |
| Auth | JWT (python-jose, bcrypt) |
| Email | Resend API |
| Scheduling | APScheduler |
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
| GET | `/products/{id}` | Get a single product |
| PUT | `/products/{id}` | Update product details |
| DELETE | `/products/{id}` | Delete a product |

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
React Frontend (Vercel)
↓
FastAPI REST API (Render)
↓
PostgreSQL Database (Neon)
↓
Resend API → Email receipts to seller
APScheduler → Daily 8AM low-stock & expiry alerts

---

## Local Development

```bash
# Clone the repo
git clone https://github.com/Khine12/inventra.git
cd inventra

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your values

# Run the server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v
```

---

## Environment Variables
DATABASE_URL=your_neon_postgresql_connection_string
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RESEND_API_KEY=your_resend_api_key

---

## CI/CD

GitHub Actions automatically runs the full pytest suite on every push to `main`. All 9 tests must pass before deployment.
