import os
os.environ["DATABASE_URL"]="sqlite:///./test_fitbuddy.db"
os.environ["ADMIN_TOKEN"]="test-token"
os.environ["ADMIN_SESSION_SECRET"]="test-secret"
from fastapi.testclient import TestClient
from app.main import app

def test_home():
    with TestClient(app) as c:
        r=c.get("/")
        assert r.status_code==200
        assert "FitBuddy" in r.text

def test_admin_protected():
    with TestClient(app) as c:
        r=c.get("/view-all-users",follow_redirects=False)
        assert r.status_code==303
        assert r.headers["location"]=="/admin/login"

def test_missing_user():
    with TestClient(app) as c:
        assert c.get("/api/users/not-found").status_code==404
