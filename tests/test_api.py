import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import get_db
from backend.services.seed_data import seed_database_if_empty

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    db = next(get_db())
    seed_database_if_empty(db)
    db.close()

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_get_settings():
    with TestClient(app) as client:
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "system_health" in data
        assert data["system_health"]["axe_core_ready"] is True

def test_list_projects_and_overview():
    with TestClient(app) as client:
        response = client.get("/api/projects")
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) > 0  # Seeded project exists

        overview_res = client.get("/api/overview/metrics")
        assert overview_res.status_code == 200
        metrics = overview_res.json()
        assert "summary" in metrics
        assert "severity_breakdown" in metrics
        assert "trends" in metrics

def test_create_and_audit_project():
    with TestClient(app) as client:
        sample_code = """<div>
            <label for="username">Username</label>
            <input id="username" type="text">
            <button type="button">Sign In</button>
        </div>"""

        create_res = client.post("/api/projects", json={
            "name": "Automated Test Project",
            "description": "Integration test validation",
            "source_type": "html",
            "initial_source": sample_code
        })
        assert create_res.status_code == 200
        proj = create_res.json()
        project_id = proj["id"]
        revision_id = proj["revision_id"]

        # Run audit
        audit_res = client.post("/api/audits/run", json={
            "project_id": project_id,
            "revision_id": revision_id,
            "standard": "WCAG 2.2 AA"
        })
        assert audit_res.status_code == 200
        audit_data = audit_res.json()
        assert "score" in audit_data
        assert "findings" in audit_data

        # Run interaction test
        test_res = client.post("/api/tests/run", json={
            "project_id": project_id,
            "revision_id": revision_id
        })
        assert test_res.status_code == 200
        test_data = test_res.json()
        assert test_data["total_checks"] > 0

        # Generate report
        report_res = client.post("/api/reports/generate", json={
            "project_id": project_id,
            "title": "Automated Test Conformance Report"
        })
        assert report_res.status_code == 200
        report_data = report_res.json()
        assert "data" in report_data

        # Cleanup project
        del_res = client.delete(f"/api/projects/{project_id}")
        assert del_res.status_code == 200
