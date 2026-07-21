import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import storage
from ui import app as ui_app

app = ui_app.app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_redirects_to_login_when_not_authenticated(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_session_file_missing_redirects_to_login(client, monkeypatch, tmp_path):
    temp_session = tmp_path / "session.json"
    monkeypatch.setattr(storage, "SESSION_FILE", str(temp_session))

    with client.session_transaction() as sess:
        sess["user"] = {"user_id": 1, "username": "test-user"}

    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_attempts_are_rate_limited(client, monkeypatch):
    monkeypatch.setattr(ui_app, "login_user", lambda *args, **kwargs: None)
    app.config["LOGIN_ATTEMPT_LIMIT"] = 2
    app.config["LOGIN_ATTEMPT_WINDOW_SECONDS"] = 60
    ui_app.LOGIN_ATTEMPT_TRACKERS.clear()

    first = client.post(
        "/login",
        data={"username": "demo", "password": "wrong"},
        follow_redirects=True,
    )
    second = client.post(
        "/login",
        data={"username": "demo", "password": "wrong"},
        follow_redirects=True,
    )
    third = client.post(
        "/login",
        data={"username": "demo", "password": "wrong"},
        follow_redirects=True,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
