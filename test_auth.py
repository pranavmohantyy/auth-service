import pytest
from fastapi.testclient import TestClient
from main import app, SessionLocal

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_register(client):
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_login(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    response = client.post("/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_token_expiry(client):
    client.post("/register", json={"username": "testuser", "password": "testpass"})
    login_response = client.post("/login", json={"username": "testuser", "password": "testpass"})
    access_token = login_response.json()["access_token"]
    response = client.get("/protected", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    
    # Wait for token to expire
    import time
    time.sleep(3600)  # assuming token expiration is set to 1 hour

    response = client.get("/protected", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401

def test_role_access(client):
    client.post("/register", json={"username": "adminuser", "password": "adminpass"})
    # Assuming there is a way to set role during registration
    response = client.post("/login", json={"username": "adminuser", "password": "adminpass"})
    access_token = response.json()["access_token"]
    response = client.get("/admin", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
