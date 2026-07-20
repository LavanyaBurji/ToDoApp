import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import storage
from ui.app import app


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
