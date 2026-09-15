"""
tests/test_history.py
Covers history listing, filtering, stats, deletion, and CSV/PDF report
generation.
"""

import io


def _upload_and_detect(client, headers):
    data = (io.BytesIO(b"fake image"), "p.jpg")
    up = client.post(
        "/api/upload/image",
        data={"file": data},
        content_type="multipart/form-data",
        headers=headers,
    )
    detection_id = up.get_json()["detection"]["id"]
    client.post(f"/api/detect/{detection_id}", headers=headers)
    return detection_id


def test_history_empty_initially(client, auth_headers):
    resp = client.get("/api/history", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 0


def test_history_lists_after_upload(client, auth_headers):
    _upload_and_detect(client, auth_headers)
    resp = client.get("/api/history", headers=auth_headers)
    body = resp.get_json()
    assert body["total"] == 1
    assert body["detections"][0]["status"] == "processed"


def test_history_requires_auth(client):
    resp = client.get("/api/history")
    assert resp.status_code == 401


def test_history_invalid_date_filter_returns_400(client, auth_headers):
    resp = client.get("/api/history?date_from=not-a-date", headers=auth_headers)
    assert resp.status_code == 400


def test_history_valid_date_filter(client, auth_headers):
    _upload_and_detect(client, auth_headers)
    resp = client.get("/api/history?date_from=2020-01-01&date_to=2099-01-01", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 1


def test_history_severity_filter_excludes_non_matching(client, auth_headers):
    _upload_and_detect(client, auth_headers)
    # mock detector's severities are randomized; query for a severity that's
    # very unlikely to exist alongside the real one and confirm it's excluded
    # or included consistently with what /api/history (no filter) reports.
    all_resp = client.get("/api/history", headers=auth_headers)
    actual_severity = all_resp.get_json()["detections"][0]["severity"]
    other = "high" if actual_severity != "high" else "low"

    filtered = client.get(f"/api/history?severity={other}", headers=auth_headers)
    assert filtered.get_json()["total"] == 0

    matching = client.get(f"/api/history?severity={actual_severity}", headers=auth_headers)
    assert matching.get_json()["total"] == 1


def test_stats_endpoint(client, auth_headers):
    _upload_and_detect(client, auth_headers)
    resp = client.get("/api/history/stats", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total_scans"] == 1
    assert "severity_breakdown" in body


def test_delete_detection(client, auth_headers):
    detection_id = _upload_and_detect(client, auth_headers)
    resp = client.delete(f"/api/history/{detection_id}", headers=auth_headers)
    assert resp.status_code == 200

    resp2 = client.get("/api/history", headers=auth_headers)
    assert resp2.get_json()["total"] == 0


def test_delete_nonexistent_detection(client, auth_headers):
    resp = client.delete("/api/history/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_csv_report_with_no_history_returns_404(client, auth_headers):
    resp = client.get("/api/report/csv", headers=auth_headers)
    assert resp.status_code == 404


def test_csv_report_generation(client, auth_headers):
    _upload_and_detect(client, auth_headers)
    resp = client.get("/api/report/csv", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/csv")


def test_pdf_report_generation(client, auth_headers):
    _upload_and_detect(client, auth_headers)
    resp = client.get("/api/report/pdf", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/pdf"


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
