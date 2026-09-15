-- schema.sql
-- Raw SQL version of the database, matching the whiteboard ER diagram exactly.
-- The Flask app creates these automatically via SQLAlchemy (database/init_db.py),
-- but this file is here for documentation, manual setup, and Anushka/Ayushi
-- to reference without needing to read Python.

CREATE DATABASE IF NOT EXISTS pothole_ai;
USE pothole_ai;

CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,       -- bcrypt hash
    role        VARCHAR(20)  NOT NULL DEFAULT 'user',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS detections (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    image_path     VARCHAR(255),
    video_path     VARCHAR(255),
    latitude       FLOAT,
    longitude      FLOAT,
    confidence     FLOAT,
    severity       VARCHAR(20),
    pothole_count  INT DEFAULT 0,
    status         VARCHAR(20) DEFAULT 'pending',
    detected_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS potholes (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    detection_id   INT NOT NULL,
    x_min          FLOAT NOT NULL,
    y_min          FLOAT NOT NULL,
    x_max          FLOAT NOT NULL,
    y_max          FLOAT NOT NULL,
    width          FLOAT,
    height         FLOAT,
    size           FLOAT,
    confidence     FLOAT NOT NULL,
    severity       VARCHAR(20),
    FOREIGN KEY (detection_id) REFERENCES detections(id) ON DELETE CASCADE
);

CREATE INDEX idx_detections_user ON detections(user_id);
CREATE INDEX idx_potholes_detection ON potholes(detection_id);
