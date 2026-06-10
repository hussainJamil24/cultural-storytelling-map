"""Tests for registration and login."""
from conftest import login, register


def test_register_succeeds(client):
    res = register(client)
    assert res.status_code == 201
    assert res.json()["message"] == "User registered successfully"


def test_register_duplicate_email_rejected(client):
    register(client, email="dupe@example.com")
    res = register(client, email="dupe@example.com")
    assert res.status_code == 409  # Conflict


def test_login_returns_token(client):
    register(client, email="login@example.com", password="secret123")
    res = login(client, email="login@example.com", password="secret123")
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_rejected(client):
    register(client, email="wrong@example.com", password="correct")
    res = login(client, email="wrong@example.com", password="WRONG")
    assert res.status_code == 401


def test_login_unknown_email_rejected(client):
    res = login(client, email="nobody@example.com", password="whatever")
    assert res.status_code == 401


def test_new_user_is_not_admin(client):
    register(client, email="regular@example.com")
    res = login(client, email="regular@example.com")
    assert res.json()["is_admin"] is False
