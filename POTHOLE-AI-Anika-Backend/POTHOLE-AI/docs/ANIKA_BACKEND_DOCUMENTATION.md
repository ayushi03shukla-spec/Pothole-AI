# Anika's Backend — API Documentation

Base URL (local): `http://localhost:5000`
All request/response bodies are JSON unless uploading a file (multipart/form-data).
Protected routes require header: `Authorization: Bearer <token>`

---

## Auth

### POST `/api/auth/register`
```json
// Request
{ "name": "Anika", "email": "anika@example.com", "password": "secure123" }

// Response 201
{
  "message": "Account created successfully",
  "token": "eyJ...",
  "user": { "id": 1, "name": "Anika", "email": "anika@example.com", "role": "user", "created_at": "..." }
}
```

### POST `/api/auth/login`
```json
// Request
{ "email": "anika@example.com", "password": "secure123" }
// Response 200 — same shape as register
```

### GET `/api/auth/me`  (protected)
Returns the current logged-in user.

---

## Upload

### POST `/api/upload/image`  (protected, multipart/form-data)
Fields: `file` (jpg/jpeg/png), optional `latitude`, `longitude`

```json
// Response 201
{
  "message": "Image uploaded successfully. Call /api/detect/<id> to run detection.",
  "detection": { "id": 5, "status": "pending", "image_path": "...", ... }
}
```

### POST `/api/upload/video`  (protected)
Same as above, fields: mp4/mov/avi.

---

## Detection

### POST `/api/detect/<detection_id>`  (protected)
Runs the model (mock now, real YOLO after Ayushi's handover) on the uploaded
file and stores every pothole found.

```json
// Response 200
{
  "message": "Detection complete",
  "detection": {
    "id": 5, "status": "processed", "pothole_count": 2,
    "confidence": 0.81, "severity": "medium",
    "potholes": [
      { "id": 1, "bbox": {"x_min":10,"y_min":20,"x_max":90,"y_max":110}, "confidence": 0.79, "severity": "medium" },
      { "id": 2, "bbox": {"x_min":150,"y_min":40,"x_max":220,"y_max":130}, "confidence": 0.83, "severity": "medium" }
    ]
  }
}
```

### GET `/api/detect/<detection_id>`  (protected)
Fetch one detection with its potholes. 403 if it doesn't belong to you.

---

## History

### GET `/api/history`  (protected)
Query params (all optional): `severity`, `date_from` (YYYY-MM-DD), `date_to`, `page`, `per_page`

```json
{
  "detections": [ { "id": 5, "severity": "medium", ... } ],
  "page": 1, "per_page": 20, "total": 1, "total_pages": 1
}
```

### GET `/api/history/stats`  (protected)
```json
{ "total_scans": 12, "total_potholes_found": 27, "severity_breakdown": {"low":5,"medium":4,"high":3} }
```

### DELETE `/api/history/<detection_id>`  (protected)

---

## Reports

### GET `/api/report/csv`  (protected)
Downloads a CSV file of all the user's detections.

### GET `/api/report/pdf`  (protected)
Downloads a formatted PDF table of all the user's detections.

Both return **404** if the user has no history yet.

---

## Health

### GET `/api/health`
```json
{ "status": "ok", "service": "pothole-ai-backend" }
```
Used by Render/Railway deployment health checks (Phase 6).

---

## Error format
Every error follows the same shape so the frontend can handle them generically:
```json
{ "error": "human readable message" }
```

| Status | Meaning |
|---|---|
| 400 | Bad request / validation failed |
| 401 | Missing or invalid JWT |
| 403 | Valid JWT, but not the owner of this resource |
| 404 | Resource not found |
| 409 | Conflict (e.g. duplicate email) |
| 413 | File too large |
| 500 | Server error |

---

## Integration notes for teammates

**Anamika (Frontend):** Upload page → `POST /api/upload/image`, then immediately
`POST /api/detect/<id>` to show results. Dashboard → `GET /api/history/stats`.
History page → `GET /api/history` with filters. Report buttons → the two
`/api/report/*` endpoints (these return actual file downloads, not JSON —
point an `<a href>` or `window.open()` at them with the auth token as a query
param or via a fetch+blob download).

**Prashant (Maps):** `GET /api/history` gives you `latitude`, `longitude`,
`severity` per detection — plot directly as Folium/Leaflet markers, color by
`severity`.

**Ayushi (AI Model):** Replace `utils/mock_detector.py`'s `run_detection()`
with real YOLOv8 inference. Keep the return shape
`[{x_min, y_min, x_max, y_max, confidence}, ...]` identical and nothing else
in the backend needs to change.
