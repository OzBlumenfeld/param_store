import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.core.database import get_db, Base
import os

# Use in-memory database for faster and more isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

def test_register_and_login(client):
    # 1. Register
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

    # 2. Register same user again (should fail)
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 400

    # 3. Login
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

    # 4. Login with wrong password
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
