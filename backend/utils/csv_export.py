"""
utils/csv_export.py
Builds a CSV report of a user's detection history using pandas.
"""

import os
import uuid
import pandas as pd


def generate_csv_report(detections: list, report_folder: str) -> str:
    """
    detections: list of Detection.to_dict() results
    Returns the full path of the generated CSV file.
    """
    rows = []
    for d in detections:
        rows.append({
            "Detection ID": d["id"],
            "Date": d["detected_at"],
            "Image": d["image_path"] or "",
            "Video": d["video_path"] or "",
            "Latitude": d["latitude"],
            "Longitude": d["longitude"],
            "Pothole Count": d["pothole_count"],
            "Confidence": d["confidence"],
            "Severity": d["severity"],
            "Status": d["status"],
        })

    df = pd.DataFrame(rows)

    os.makedirs(report_folder, exist_ok=True)
    filename = f"pothole_report_{uuid.uuid4().hex[:8]}.csv"
    full_path = os.path.join(report_folder, filename)
    df.to_csv(full_path, index=False)

    return full_path
