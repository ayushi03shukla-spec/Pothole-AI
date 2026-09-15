import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

BACKEND_URL = "http://127.0.0.1:5000"


def get_headers(token):
    return {"Authorization": f"Bearer {token}"}


def get_stats(token):
    """Fetch real dashboard statistics from Flask."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/history/stats",
            headers=get_headers(token),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def get_history(token):
    """Fetch real detection history from Flask."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/history",
            headers=get_headers(token),
            params={"page": 1, "per_page": 1000},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def get_backend_health():
    """Check whether the Flask backend is reachable."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/health",
            timeout=5,
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def format_location(latitude, longitude):
    if latitude is None or longitude is None:
        return "Not available"

    return f"{float(latitude):.6f}, {float(longitude):.6f}"


def format_datetime(value):
    if not value:
        return "Unknown"

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(value)


def show():
    """Display dashboard using real backend data."""

    st.markdown("# Dashboard")
    st.markdown("Pothole AI Detection System")

    token = st.session_state.get("token")

    if not token:
        st.warning("Please log in to view the dashboard.")
        return

    user = st.session_state.get("user", {})

    if user:
        user_name = user.get("name")
        if user_name:
            st.info(f"Welcome, {user_name}!")

    # ------------------------------------------------------------
    # Load backend data
    # ------------------------------------------------------------

    stats = get_stats(token)
    history_data = get_history(token)

    if stats is None or history_data is None:
        st.error(
            "Could not load dashboard data from the Flask backend."
        )
        return

    detections = history_data.get("detections", [])

    # ------------------------------------------------------------
    # Prepare real data
    # ------------------------------------------------------------

    total_scans = int(stats.get("total_scans", 0))
    total_potholes = int(stats.get("total_potholes_found", 0))

    severity_breakdown = stats.get(
        "severity_breakdown",
        {
            "low": 0,
            "medium": 0,
            "high": 0,
        },
    )

    high_count = int(severity_breakdown.get("high", 0))
    medium_count = int(severity_breakdown.get("medium", 0))
    low_count = int(severity_breakdown.get("low", 0))

    undetermined_count = sum(
        1
        for detection in detections
        if (detection.get("severity") or "").lower()
        == "undetermined"
    )

    processed_count = sum(
        1
        for detection in detections
        if (detection.get("status") or "").lower()
        == "processed"
    )

    pending_count = sum(
        1
        for detection in detections
        if (detection.get("status") or "").lower()
        == "pending"
    )

    failed_count = sum(
        1
        for detection in detections
        if (detection.get("status") or "").lower()
        == "failed"
    )

    confidence_values = []

    for detection in detections:
        confidence = detection.get("confidence")

        if confidence is not None:
            confidence_values.append(
                float(confidence) * 100
            )

    avg_confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values
        else 0.0
    )

    # ------------------------------------------------------------
    # Statistics cards
    # ------------------------------------------------------------

    st.markdown("## Statistics Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Scans",
            value=total_scans,
        )

    with col2:
        st.metric(
            label="Potholes Found",
            value=total_potholes,
        )

    with col3:
        st.metric(
            label="High Severity",
            value=high_count,
        )

    with col4:
        st.metric(
            label="Pending",
            value=pending_count,
        )

    # ------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------

    st.markdown("## Analytics")

    col1, col2 = st.columns(2)

    # ------------------------------------------------------------
    # Severity chart
    # ------------------------------------------------------------

    with col1:
        st.markdown("### Detections by Severity")

        severity_df = pd.DataFrame(
            {
                "Severity": [
                    "Low",
                    "Medium",
                    "High",
                    "Undetermined",
                ],
                "Count": [
                    low_count,
                    medium_count,
                    high_count,
                    undetermined_count,
                ],
            }
        )

        fig_severity = go.Figure(
            data=[
                go.Bar(
                    x=severity_df["Severity"],
                    y=severity_df["Count"],
                )
            ]
        )

        fig_severity.update_layout(
            title="Detection Severity Distribution",
            xaxis_title="Severity",
            yaxis_title="Number of Detections",
            height=400,
        )

        st.plotly_chart(
            fig_severity,
            use_container_width=True,
        )

    # ------------------------------------------------------------
    # Status chart
    # ------------------------------------------------------------

    with col2:
        st.markdown("### Detections by Status")

        status_df = pd.DataFrame(
            {
                "Status": [
                    "Processed",
                    "Pending",
                    "Failed",
                ],
                "Count": [
                    processed_count,
                    pending_count,
                    failed_count,
                ],
            }
        )

        fig_status = go.Figure(
            data=[
                go.Pie(
                    labels=status_df["Status"],
                    values=status_df["Count"],
                    hole=0.35,
                )
            ]
        )

        fig_status.update_layout(
            title="Detection Processing Status",
            height=400,
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True,
        )

    # ------------------------------------------------------------
    # Second analytics row
    # ------------------------------------------------------------

    col1, col2 = st.columns(2)

    # ------------------------------------------------------------
    # Last 7 days trend
    # ------------------------------------------------------------

    with col1:
        st.markdown("### Weekly Trend")

        today = datetime.now().date()
        last_7_days = [
            today - timedelta(days=i)
            for i in range(6, -1, -1)
        ]

        daily_counts = {
            day: 0
            for day in last_7_days
        }

        for detection in detections:
            detected_at = detection.get("detected_at")

            if not detected_at:
                continue

            try:
                dt = datetime.fromisoformat(
                    detected_at.replace("Z", "+00:00")
                )

                detection_day = dt.date()

                if detection_day in daily_counts:
                    daily_counts[detection_day] += 1

            except (ValueError, TypeError):
                continue

        trend_dates = [
            day.strftime("%a")
            for day in last_7_days
        ]

        trend_values = [
            daily_counts[day]
            for day in last_7_days
        ]

        fig_trend = go.Figure()

        fig_trend.add_trace(
            go.Scatter(
                x=trend_dates,
                y=trend_values,
                mode="lines+markers",
            )
        )

        fig_trend.update_layout(
            title="Detection Trend - Last 7 Days",
            xaxis_title="Day",
            yaxis_title="Number of Scans",
            height=400,
        )

        st.plotly_chart(
            fig_trend,
            use_container_width=True,
        )

    # ------------------------------------------------------------
    # Confidence distribution
    # ------------------------------------------------------------

    with col2:
        st.markdown("### Confidence Distribution")

        confidence_ranges = [
            "50-60%",
            "60-70%",
            "70-80%",
            "80-90%",
            "90-100%",
        ]

        confidence_counts = [0, 0, 0, 0, 0]

        for confidence in confidence_values:

            if 50 <= confidence < 60:
                confidence_counts[0] += 1
            elif 60 <= confidence < 70:
                confidence_counts[1] += 1
            elif 70 <= confidence < 80:
                confidence_counts[2] += 1
            elif 80 <= confidence < 90:
                confidence_counts[3] += 1
            elif 90 <= confidence <= 100:
                confidence_counts[4] += 1

        confidence_df = pd.DataFrame(
            {
                "Range": confidence_ranges,
                "Count": confidence_counts,
            }
        )

        fig_confidence = go.Figure(
            data=[
                go.Bar(
                    x=confidence_df["Range"],
                    y=confidence_df["Count"],
                )
            ]
        )

        fig_confidence.update_layout(
            title="AI Model Confidence Levels",
            xaxis_title="Confidence Range",
            yaxis_title="Number of Detections",
            height=400,
        )

        st.plotly_chart(
            fig_confidence,
            use_container_width=True,
        )

    # ------------------------------------------------------------
    # Recent detections
    # ------------------------------------------------------------

    st.markdown("## Recent Detections")

    recent_rows = []

    for detection in detections[:5]:

        confidence = detection.get("confidence")

        if confidence is not None:
            confidence_display = (
                f"{float(confidence) * 100:.2f}%"
            )
        else:
            confidence_display = "N/A"

        recent_rows.append(
            {
                "ID": f"D{detection.get('id', '')}",
                "Location": format_location(
                    detection.get("latitude"),
                    detection.get("longitude"),
                ),
                "Severity": str(
                    detection.get("severity")
                    or "undetermined"
                ).capitalize(),
                "Confidence": confidence_display,
                "Status": str(
                    detection.get("status")
                    or "unknown"
                ).capitalize(),
                "Potholes": detection.get(
                    "pothole_count",
                    0,
                ),
                "Date": format_datetime(
                    detection.get("detected_at")
                ),
            }
        )

    if recent_rows:
        df_recent = pd.DataFrame(recent_rows)

        st.dataframe(
            df_recent,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No detections have been recorded yet.")

    # ------------------------------------------------------------
    # Quick actions
    # ------------------------------------------------------------

    st.markdown("## Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "Upload Image",
            use_container_width=True,
        ):
            st.session_state.page = "detection"
            st.rerun()

    with col2:
        if st.button(
            "View Map",
            use_container_width=True,
        ):
            st.session_state.page = "map"
            st.rerun()

    with col3:
        if st.button(
            "History",
            use_container_width=True,
        ):
            st.session_state.page = "history"
            st.rerun()

    with col4:
        if st.button(
            "Generate Report",
            use_container_width=True,
        ):
            st.session_state.page = "reports"
            st.rerun()

    # ------------------------------------------------------------
    # System health
    # ------------------------------------------------------------

    st.markdown("## System Health")

    backend_ok = get_backend_health()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info(
            "**API Status**\n\n"
            + ("Connected" if backend_ok else "Unavailable")
        )

    with col2:
        st.info(
            "**Database**\n\n"
            "Connected through backend"
            if backend_ok
            else
            "**Database**\n\nUnavailable"
        )

    with col3:
        st.info(
            "**ML Pipeline**\n\n"
            "Integrated"
            if backend_ok
            else
            "**ML Pipeline**\n\nUnavailable"
        )

    with col4:
        st.info(
            "**Processed Scans**\n\n"
            f"{processed_count}"
        )
