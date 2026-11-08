from fastapi.testclient import TestClient

from app import main
from app.main import app

client = TestClient(app)


class FakeConnection:
    # pretends to be a database connection that works
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query):
        return None


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ready_when_database_is_up(monkeypatch):
    monkeypatch.setattr(main, "DATABASE_URL", "postgresql://fake")
    monkeypatch.setattr(main, "get_connection", lambda: FakeConnection())

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_returns_503_when_database_is_down(monkeypatch):
    monkeypatch.setattr(main, "DATABASE_URL", "postgresql://nobody@localhost:1/none")

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}


def test_ready_returns_503_when_database_not_configured(monkeypatch):
    monkeypatch.setattr(main, "DATABASE_URL", None)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "database not configured"}


def test_root_returns_service_info():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "sre-platform"
