import os
import sys
from pathlib import Path

import bcrypt
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PASSWORD = "rahasia-test"
ADMIN_KEY = "admin-test-key"


@pytest.fixture(scope="session")
def tmp_root(tmp_path_factory):
    return tmp_path_factory.mktemp("backend")


@pytest.fixture(scope="session")
def client(tmp_root):
    # TEST_DATABASE_URL: jalankan test di DB yang sudah di-migrate (mis. Postgres kosong)
    os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{tmp_root / 'test.db'}"
    os.environ["JWT_SECRET"] = "test-secret"
    os.environ["SHARED_PASSWORD_HASH"] = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(4)).decode()
    os.environ["ADMIN_API_KEY"] = ADMIN_KEY

    from fastapi.testclient import TestClient
    from app.core.config import settings
    settings.STORAGE_ROOT = tmp_root / "data"
    settings.POSTURE_DIR = settings.STORAGE_ROOT / "uploads" / "posture"
    settings.LOGS_DIR = settings.STORAGE_ROOT / "logs"

    from app.db.session import SessionLocal, engine
    from app.models import Base, User
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add_all([User(user_email="peserta@test.com", name="Peserta"), User(user_email="lain@test.com")])
        db.commit()

    from app.main import app
    return TestClient(app)


def login(client, email="peserta@test.com", password=PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


@pytest.fixture
def auth(client):
    token = login(client).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin():
    return {"X-API-Key": ADMIN_KEY}
