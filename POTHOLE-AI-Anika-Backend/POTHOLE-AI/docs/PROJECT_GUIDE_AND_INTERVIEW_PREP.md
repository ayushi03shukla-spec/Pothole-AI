# Pothole AI Project Guide

## 1. Project overview

The Pothole AI project is a full-stack system designed to help cities and local agencies detect potholes from uploaded images or videos, store the results, and generate reports for tracking and decision-making.

The backend portion built in this repository focuses on:

- user authentication and authorization
- file upload handling
- pothole detection workflow
- storing detections and pothole metadata
- history and reporting
- deployment-ready health checks

This project is designed in phases so the team can work in parallel. While the AI model is being trained, the backend already supports mock detection data so the rest of the system can be built and tested without waiting for the final ML model.

---

## 2. Why this project exists

Potholes are a common infrastructure issue that can cause:

- road accidents
- vehicle damage
- expensive maintenance
- public safety concerns

A system that can:

- accept road images or videos
- identify potholes automatically
- show severity and damage patterns
- save history for users and authorities
- export data in CSV/PDF format

can make maintenance planning much more efficient.

The backend is the core connection point between:

- the frontend interface
- the AI detection engine
- the database
- reporting tools
- deployment infrastructure

---

## 3. Project architecture

The project follows a layered architecture:

### 3.1 Presentation layer
This is the user-facing part, such as a React or Streamlit frontend. It calls the backend APIs.

### 3.2 API layer
The Flask application exposes endpoints for:

- authentication
- upload
- detection processing
- history queries
- CSV/PDF reports
- health checks

### 3.3 Business logic layer
This includes functions such as:

- validating uploads
- generating JWT tokens
- creating detection records
- running detection logic
- exporting reports

### 3.4 Data layer
The database stores:

- users
- uploaded detections
- pothole bounding boxes and metadata

### 3.5 Utility layer
Utility files handle tasks like:

- file management
- mock detection logic
- CSV export
- PDF export
- password hashing and JWT authentication

---

## 4. Folder structure and purpose

```text
POTHOLE-AI/
├── README_ANIKA.md
├── Makefile
├── backend/
│   ├── app.py
│   ├── run.py
│   ├── config.py
│   ├── extensions.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env
│   ├── database/
│   │   ├── init_db.py
│   │   ├── schema.sql
│   │   └── seed_data.py
│   ├── models/
│   │   ├── user.py
│   │   ├── detection.py
│   │   └── pothole.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── upload_routes.py
│   │   ├── detection_routes.py
│   │   ├── history_routes.py
│   │   └── report_routes.py
│   ├── utils/
│   │   ├── auth_utils.py
│   │   ├── csv_export.py
│   │   ├── file_handler.py
│   │   ├── mock_detector.py
│   │   └── pdf_export.py
│   ├── uploads/
│   │   ├── images/
│   │   └── videos/
│   ├── static/
│   │   └── reports/
│   └── tests/
│       ├── test_auth.py
│       ├── test_upload.py
│       └── test_history.py
├── docs/
│   ├── ANIKA_BACKEND_DOCUMENTATION.md
│   └── PROJECT_GUIDE_AND_INTERVIEW_PREP.md
└── .gitignore
```

### Key files explained

#### app.py
This is the Flask application factory. It creates the app, initializes extensions, and registers all route blueprints.

#### run.py
This is the entry point. It starts the Flask server on a given host and port.

#### config.py
This file contains project settings, including:

- secret keys
- database URL
- upload size limits
- allowed file types
- CORS setup

#### extensions.py
This centralizes shared Flask extensions including:

- database instance
- JWT
- CORS
- bcrypt utilities

#### models/
These files define the database schema using SQLAlchemy models.

#### routes/
Each file groups related endpoints. This keeps the API organized and easier to scale.

#### utils/
This folder contains helper modules for repeated logic, such as JWT helpers, CSV/PDF generation, and mock detection.

---

## 5. Project flow: how the backend works

### Step 1: User registers or logs in

The user creates an account using the register endpoint or logs in using the login endpoint.

- Passwords are hashed before saving.
- JWT tokens are generated for authenticated routes.
- The user ID is attached to the token, which is then used to verify ownership.

### Step 2: User uploads image/video

The frontend sends multipart form data containing the file and optional location fields.

The server:

- validates the file extension
- creates a database record for the upload
- saves the file in the appropriate upload folder
- returns the detection ID to the client

### Step 3: Detection is triggered

When the client calls the detection endpoint, the backend:

- fetches the stored detection by ID
- confirms the detection belongs to the logged-in user
- runs the detection logic
- saves pothole bounding boxes and metadata into the database
- marks the detection as processed

### Step 4: History is generated

The system stores all user scans with:

- timestamp
- severity
- file type
- confidence
- coordinates if provided
- pothole count

This is important for both auditing and frontend dashboard features.

### Step 5: Reports are exported

The backend can export user history as:

- CSV file
- PDF report

This allows the frontend or admin users to download a historical summary.

---

## 6. Database design and why it is structured this way

The backend uses three main tables:

### User
Stores account data such as:

- name
- email
- password hash
- created timestamp

### Detection
Stores one uploaded file analysis lifecycle. One detection represents one uploaded image or video.

Example columns include:

- user_id
- file_path
- file_type
- status
- severity
- confidence
- created timestamp

### Pothole
Stores every pothole found in a detection.

Example columns include:

- detection_id
- bounding box coordinates
- confidence
- severity
- description or metadata

This structure separates the detection record from individual pothole results. That is important because one uploaded image may contain multiple potholes.

---

## 7. Why SQLite is used for local development

The backend is configured so that the project can run locally without an installed MySQL server.

Reasons:

- easier onboarding for beginners
- faster development setup
- zero external database dependency
- safe for local testing and demonstration

When needed for production or a shared environment, the project can switch to MySQL using the database variables in `.env`.

---

## 8. Why the mock detector exists

The project was intentionally designed so that the model can be swapped in later without changing the API contract.

The file `backend/utils/mock_detector.py` returns realistic fake pothole predictions. This lets the rest of the application behave like a real detection pipeline while the actual YOLO model is still being trained.

This is a strong engineering choice because it separates:

- backend API logic
- model integration logic
- database logic

The backend contract stays stable even if the actual detector changes.

---

## 9. Security design

The backend includes important security behavior:

### JWT authentication
Every protected route requires a valid access token.

### Password hashing
Passwords are never stored in plain text.

### User ownership validation
Users can only access their own detections and reports.

### File validation
Only allowed file types are accepted:

- images: png, jpg, jpeg
- videos: mp4, mov, avi

### Upload size limits
The backend restricts file size for safety.

---

## 10. Why the routes are separated by responsibility

The project uses route blueprints so responsibility is cleanly divided:

- auth routes: login/register and user identity
- upload routes: file handling
- detection routes: AI processing and result retrieval
- history routes: listing, filtering, deleting history
- report routes: CSV/PDF export

This separation makes the code easier to:

- test
- extend
- maintain
- onboard new developers

---

## 11. How the app starts

The app starts from `backend/run.py`:

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

This is a development server setup. For production deployments, a WSGI server such as Gunicorn is recommended.

---

## 12. How the environment is configured

The file `backend/config.py` reads environment variables so secrets and database settings are not hardcoded.

Example settings include:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- database URL from MySQL or SQLite
- upload folder paths
- CORS settings

This keeps the code portable across local, test, and production environments.

---

## 13. Typical end-to-end flow

1. User signs up/logs in.
2. User uploads an image/video.
3. Backend saves the file and creates a detection record.
4. Backend calls detection logic.
5. Pothole data is stored in the database.
6. User views history and statistics.
7. User downloads the CSV or PDF report.
8. The frontend often displays the detections on a dashboard or map.

This is the true lifecycle of the project.

---

## 14. How the project is meant to evolve

This project is intentionally structured for phased implementation.

### Phase 1: backend foundation
- auth
- upload
- database
- history
- reporting

### Phase 2: mock-based development
- use realistic sample detection data
- frontend can build around expected API responses

### Phase 3: AI integration
- replace mock detector with real YOLO model
- keep response format stable

### Phase 4: expansion
- add map visualization
- improve admin reporting
- add more analytics

---

## 15. Interview questions and answers

### Q1: What is the purpose of this project?

A: The project is a pothole detection and tracking system. It allows users to upload road images or videos, run detection, store the results, and review historical data and reports.

### Q2: Why is the backend separate from the AI model?

A: The backend handles the API, database, authentication, uploads, and business logic. The model is responsible for identifying potholes. Keeping them separate makes the system easier to maintain and allows swapping the model later without changing the API contract.

### Q3: Why do we use JWT?

A: JWT provides a compact and secure way to authenticate API requests. The backend can verify the user identity on every protected route without needing session cookies.

### Q4: Why are there separate tables for detection and pothole?

A: A single uploaded image can contain multiple potholes. The detection table stores the overall scan, while the pothole table stores each individual detection found in that scan.

### Q5: Why use SQLite for local development?

A: SQLite removes the dependency on a running MySQL service during local development. This makes onboarding easier and keeps the project runnable on a developer machine without extra database setup.

### Q6: What is the benefit of using a mock detector initially?

A: It allows the rest of the system to be built and tested before the real model is ready. The API contract stays stable, and only the detection logic needs to be swapped later.

### Q7: What is the role of `config.py`?

A: It centralizes configuration and environment variables, including database URLs, secrets, upload settings, and CORS rules. This reduces hardcoded values and improves security.

### Q8: Why are file uploads validated?

A: Validation helps prevent unsupported file types, malicious uploads, and disk misuse. It also makes the app more robust and predictable.

### Q9: How does the app protect user data?

A: It hashes passwords, authenticates with JWT, and enforces ownership checks to ensure users can only access their own detection data and reports.

### Q10: What is the significance of the health endpoint?

A: It provides a lightweight check for deployment tools and monitoring systems to confirm that the backend is running correctly.

### Q11: Why is `report_routes.py` important?

A: It provides business-friendly output for reporting, making it easier for users or administrators to download CSV/PDF summaries of findings.

### Q12: What is the difference between `upload` and `detect` stages?

A: The upload stage stores the file and creates a detection record. The detect stage actually processes the uploaded file and adds pothole details to the record.

### Q13: How would you integrate the real YOLO model?

A: Replace the logic inside the mock detector with YOLO inference, while preserving the same output schema. The routes and database models would remain the same.

### Q14: Why do we store coordinates and severity data?

A: This supports map visualization, maintenance prioritization, and analytics. It also helps downstream systems decide where intervention is needed first.

### Q15: What would you improve next in this project?

A: I would add deeper validation, more analytics endpoints, better deployment handling, stronger admin controls, and a real model integration pipeline with monitoring.

---

## 16. Short project summary for interviews

This project is a Flask-based pothole detection backend that lets users upload road data, process it through a detection pipeline, store findings in a database, view detection history, and generate reports. It uses JWT-based security, SQLite for local development, and a modular design that allows smooth model replacement in future phases.

---

## 17. Final takeaway

The most important idea in this project is the separation of concerns:

- API layer handles requests
- database layer handles persistence
- utility layer handles reusable logic
- AI model layer can change without breaking the app

This makes the project scalable, maintainable, and suitable for real-world use.
