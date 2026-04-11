import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Inventra API is running"}

def test_register():
    response = client.post("/auth/register", json={
        "email": "pytest@test.com",
        "full_name": "Pytest User",
        "password": "testpassword123"
    })
    assert response.status_code in [200, 400]

def test_login_invalid():
    response = client.post("/auth/login", data={
        "username": "wrong@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_valid():
    client.post("/auth/register", json={
        "email": "logintest@test.com",
        "full_name": "Login Test",
        "password": "testpassword123"
    })
    response = client.post("/auth/login", data={
        "username": "logintest@test.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def get_token():
    client.post("/auth/register", json={
        "email": "producttest@test.com",
        "full_name": "Product Test",
        "password": "testpassword123"
    })
    response = client.post("/auth/login", data={
        "username": "producttest@test.com",
        "password": "testpassword123"
    })
    return response.json()["access_token"]

def test_create_product():
    token = get_token()
    response = client.post("/products/", json={
        "name": "Test Product",
        "sku": "TP-001",
        "quantity": 100,
        "price": 9.99,
        "low_stock_threshold": 10
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"

def test_get_products():
    token = get_token()
    response = client.get("/products/",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_negative_stock_guard():
    token = get_token()
    client.post("/products/", json={
        "name": "Low Stock Item",
        "sku": "LS-001",
        "quantity": 5,
        "price": 1.99,
        "low_stock_threshold": 2
    }, headers={"Authorization": f"Bearer {token}"})
    products = client.get("/products/",
        headers={"Authorization": f"Bearer {token}"}).json()
    product_id = products[-1]["id"]
    response = client.post("/transactions/", json={
        "product_id": product_id,
        "type": "sale",
        "quantity": 999,
        "note": "Should fail"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400

def test_dashboard():
    token = get_token()
    response = client.get("/alerts/dashboard",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "low_stock_count" in data
    assert "expiring_soon_count" in data

def test_unauthorized_access():
    response = client.get("/products/")
    assert response.status_code == 401