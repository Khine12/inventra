import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, products, transactions, alerts
from app import scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventra API", version="1.0.0")

_frontend_url = os.getenv("FRONTEND_URL", "https://inventra-frontend-alpha.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[_frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(alerts.router)

@app.get("/")
def root():
    return {"message": "Inventra API is running"}