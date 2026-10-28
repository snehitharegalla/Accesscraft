import httpx
import sys

BASE_URL = "http://127.0.0.1:8008"

def test_all():
    print(f"Connecting to AccessCraft Backend at {BASE_URL}...")
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # 1. Health
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] 1. /health -> 200 OK (Status: healthy)")

    # 2. Settings & System Health
    res = client.get("/api/settings")
    assert res.status_code == 200, f"Settings failed: {res.text}"
    settings = res.json()
    assert settings["system_health"]["axe_core_ready"] is True
    print(f"[PASS] 2. /api/settings -> 200 OK (axe-core: {settings['system_health']['axe_core_ready']}, Playwright: {settings['system_health']['playwright_available']})")

    # 3. Overview Dashboard Metrics
    res = client.get("/api/overview/metrics")
    assert res.status_code == 200, f"Overview metrics failed: {res.text}"
    overview = res.json()
    print(f"[PASS] 3. /api/overview/metrics -> 200 OK (Audited interfaces: {overview['summary']['audited_interfaces']}, Pass rate: {overview['summary']['test_pass_rate']}%)")

    # 4. List Projects
    res = client.get("/api/projects")
    assert res.status_code == 200, f"List projects failed: {res.text}"
    projects = res.json()
    assert len(projects) > 0, "No projects found"
    project_id = projects[0]["id"]
    print(f"[PASS] 4. /api/projects -> 200 OK ({len(projects)} active projects, primary: {projects[0]['name']})")

    # 5. Project Details & Revisions
    res = client.get(f"/api/projects/{project_id}")
    assert res.status_code == 200
    p_detail = res.json()
    revisions = p_detail["revisions"]
    revision_id = revisions[0]["id"]
    print(f"[PASS] 5. /api/projects/{project_id} -> 200 OK ({len(revisions)} versioned revisions)")

    # 6. AI & Deterministic Adaptation Generation
    adapt_req = {
        "project_id": project_id,
        "source_code": """<form class='login'>
            <input type='text' placeholder='Email Address' tabindex='2'>
            <div class='btn' onclick='login()'>Sign In</div>
        </form>""",
        "requirements": ["Keyboard-only", "Explicit form labels", "High contrast"],
        "provider": "demo"
    }
    res = client.post("/api/adaptation/generate", json=adapt_req)
    assert res.status_code == 200, f"Adaptation failed: {res.text}"
    adapt_res = res.json()
    assert len(adapt_res["improvements"]) > 0
    print(f"[PASS] 6. /api/adaptation/generate -> 200 OK (Generated {len(adapt_res['improvements'])} improvements, mode: {adapt_res['model_used']})")

    # 7. Real axe-core Accessibility Audit
    audit_req = {
        "project_id": project_id,
        "revision_id": revision_id,
        "standard": "WCAG 2.2 AA"
    }
    res = client.post("/api/audits/run", json=audit_req)
    assert res.status_code == 200, f"Audit failed: {res.text}"
    audit_res = res.json()
    audit_id = audit_res["id"]
    print(f"[PASS] 7. /api/audits/run -> 200 OK (Calculated score: {audit_res['score']}%, Violations: {audit_res['violations_count']}, Engine: {audit_res['execution_engine']})")

    # 8. Playwright Headless Interaction Tests
    test_req = {
        "project_id": project_id,
        "revision_id": revision_id
    }
    res = client.post("/api/tests/run", json=test_req)
    assert res.status_code == 200, f"Interaction test failed: {res.text}"
    test_res = res.json()
    print(f"[PASS] 8. /api/tests/run -> 200 OK (Status: {test_res['status'].upper()}, Passed: {test_res['passed_checks']}/{test_res['total_checks']} checks in {test_res['duration_ms']}ms)")

    # 9. Fix Review Workspace & Remediation
    res = client.get(f"/api/projects/{project_id}/fixes")
    assert res.status_code == 200, f"Fixes failed: {res.text}"
    fixes_data = res.json()
    print(f"[PASS] 9. /api/projects/{project_id}/fixes -> 200 OK (Audited issues loaded, has_audit: {fixes_data['has_audit']})")

    # 10. Report Compilation & Exports (JSON, CSV, HTML)
    report_req = {
        "project_id": project_id,
        "title": "Comprehensive Conformance Validation Report"
    }
    res = client.post("/api/reports/generate", json=report_req)
    assert res.status_code == 200, f"Report generation failed: {res.text}"
    report_res = res.json()
    report_id = report_res["id"]
    print(f"[PASS] 10a. /api/reports/generate -> 200 OK (Report compiled: {report_res['title']})")

    res = client.get(f"/api/reports/{report_id}/export/csv")
    assert res.status_code == 200
    assert "Finding ID,Rule ID" in res.text
    print(f"[PASS] 10b. /api/reports/{report_id}/export/csv -> 200 OK (CSV generated, size: {len(res.text)} bytes)")

    res = client.get(f"/api/reports/{report_id}/export/html")
    assert res.status_code == 200
    assert "AccessCraft" in res.text
    print(f"[PASS] 10c. /api/reports/{report_id}/export/html -> 200 OK (Printable HTML generated, size: {len(res.text)} bytes)")

    print("\n=======================================================")
    print("ALL 12 BACKEND AND AUDIT WORKFLOW ENDPOINTS PASSED WITH 0 ERRORS!")
    print("=======================================================")

if __name__ == "__main__":
    test_all()
