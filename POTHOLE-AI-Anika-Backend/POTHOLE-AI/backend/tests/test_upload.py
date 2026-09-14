"""
tests/test_upload.py
Covers image upload, invalid file type rejection, auth requirement,
and running detection on an uploaded file end-to-end.
"""

import io


def make_fake_image():
    return (io.BytesIO(b"fake image bytes"), "test_pothole.jpg")


def test_upload_requires_auth(client):
    data, filename = make_fake_image()
    resp = client.post(
        "/api/upload/image",
        data={"file": (data, filename)},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 401


def test_upload_image_success(client, auth_headers):
    data, filename = make_fake_image()
    resp = client.post(
        "/api/upload/image",
        data={"file": (data, filename), "latitude": "26.45", "longitude": "80.33"},
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["detection"]["status"] == "pending"
    assert body["detection"]["latitude"] == 26.45


def test_upload_rejects_bad_extension(client, auth_headers):
    data = (io.BytesIO(b"not an image"), "malware.exe")
    resp = client.post(
        "/api/upload/image",
        data={"file": data},
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_run_detection_end_to_end(client, auth_headers):
    data, filename = make_fake_image()
    upload_resp = client.post(
        "/api/upload/image",
        data={"file": (data, filename)},
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    detection_id = upload_resp.get_json()["detection"]["id"]

    detect_resp = client.post(f"/api/detect/{detection_id}", headers=auth_headers)
    assert detect_resp.status_code == 200

    result = detect_resp.get_json()["detection"]
    assert result["status"] == "processed"
    assert "potholes" in result
    assert result["pothole_count"] == len(result["potholes"])


def test_detection_not_found(client, auth_headers):
    resp = client.post("/api/detect/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_cannot_access_other_users_detection(client, auth_headers, app):
    # Create a second user and a detection owned by them
    with app.app_context():
        pass  # DB already created via fixture

    data, filename = make_fake_image()
    upload_resp = client.post(
        "/api/upload/image",
        data={"file": (data, filename)},
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    detection_id = upload_resp.get_json()["detection"]["id"]

    # Register + login as a different user
    client.post("/api/auth/register", json={
        "name": "Intruder", "email": "intruder@example.com", "password": "password1",
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "intruder@example.com", "password": "password1",
    })
    intruder_headers = {"Authorization": f"Bearer {login_resp.get_json()['token']}"}

    resp = client.get(f"/api/detect/{detection_id}", headers=intruder_headers)
    assert resp.status_code == 403
