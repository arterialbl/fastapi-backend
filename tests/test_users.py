import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(".env.test")

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import UserDB

client = TestClient(app)

def test_create_user():
    email = f"{uuid.uuid4()}@example.com"

    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": email,
            "password": "123456",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == email

def test_login_user():
    import uuid

    email = f"{uuid.uuid4()}@example.com"
    password = "123456"

    client.post(
        "/users",
        json={
            "name": "Login Test",
            "email": email,
            "password": password,
        },
    )

    response = client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password():
    import uuid

    email = f"{uuid.uuid4()}@example.com"
    password = "123456"

    client.post(
        "/users",
        json={
            "name": "Wrong Password Test",
            "email": email,
            "password": password,
        },
    )

    response = client.post(
        "/login",
        data={
            "username": email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Invalid email or password"

# def test_login_inactive_user():
#     import uuid

#     email = f"{uuid.uuid4()}@example.com"
#     password = "123456"

#     response = client.post(
#         "/users",
#         json={
#             "name": "Inactive User",
#             "email": email,
#             "password": password,
#         },
#     )

#     user_id = response.json()["id"]

#     client.patch(
#         f"/users/{user_id}",
#         json={"is_active": False}
#     )

#     response = client.post(
#         "/login",
#         data={
#             "username": email,
#             "password": password,
#         },
#     )

#     assert response.status_code == 403

def test_update_user_forbidden_for_non_admin():
    email = f"{uuid.uuid4()}@example.com"
    password = "123456"

    response = client.post(
        "/users",
        json={
            "name": "User",
            "email": email,
            "password": password,
        },
    )

    user_id = response.json()["id"]

    login_response = client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        f"/users/{user_id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403

def test_get_users_for_admin():
    email = f"{uuid.uuid4()}@example.com"
    password = "123456"

    client.post(
        "/users",
        json={
            "name": "User",
            "email": email,
            "password": password,
        },
    )

    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.email == email).first()
    user.is_admin = True
    db.commit()
    db.close()

    login_response = client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

def test_get_users_pagination():
    email = f"{uuid.uuid4()}@example.com"
    password = "123456"

    client.post(
        "/users",
        json={
            "name": "Admin",
            "email": email,
            "password": password,
        },
    )

    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.email == email).first()
    user.is_admin = True
    db.commit()
    db.close()

    for i in range(5):
        client.post(
            "/users",
            json={
                "name": f"User {i}",
                "email": f"{uuid.uuid4()}@example.com",
                "password": "123456",
            },
        )

    login_response = client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users",
        params={"limit": 2, "offset": 0},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0