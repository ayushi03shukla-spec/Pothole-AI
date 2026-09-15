import requests
import streamlit as st
import pandas as pd
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:5000"


def get_history(token):
    """Fetch detection history for the logged-in user."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/history",
            headers={"Authorization": f"Bearer {token}"},
            params={"page": 1, "per_page": 1000},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        st.error(f"Could not load detection history: {exc}")
        return None


def delete_detection(detection_id, token):
    """Delete one detection from the backend."""
    try:
        response = requests.delete(
            f"{BACKEND_URL}/api/history/{detection_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        response.raise_for_status()
        return True, None

    except requests.RequestException as exc:
        return False, str(exc)


def format_location(latitude, longitude):
    """Convert GPS coordinates into a readable string."""
    if latitude is None or longitude is None:
        return "Not available"

    return f"{float(latitude):.6f}, {float(longitude):.6f}"


def format_date(value):
    """Format backend ISO datetime safely."""
    if not value:
        return "Unknown"

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(value)


def show():
    """Display real detection history from the Flask backend."""

    st.markdown("# Detection History")

    token = st.session_state.get("token")

    if not token:
        st.warning("Please log in to view your detection history.")
        return

    data = get_history(token)

    if data is None:
        return

    detections = data.get("detections", [])

    # ------------------------------------------------------------------
    # Convert backend detections into a DataFrame
    # ------------------------------------------------------------------

    rows = []

    for detection in detections:
        confidence = detection.get("confidence")
        pothole_count = detection.get("pothole_count", 0)

        if confidence is not None:
            confidence_value = round(float(confidence) * 100, 2)
        else:
            confidence_value = 0.0

        severity_raw = detection.get("severity") or "undetermined"
        severity = str(severity_raw).capitalize()

        status_raw = detection.get("status") or "unknown"
        status = str(status_raw).capitalize()

        rows.append(
            {
                "ID": f"D{detection.get('id', '')}",
                "Detection ID": detection.get("id"),
                "Location": format_location(
                    detection.get("latitude"),
                    detection.get("longitude"),
                ),
                "Severity": severity,
                "Status": status,
                "Confidence": confidence_value,
                "Potholes": int(pothole_count or 0),
                "Date": format_date(detection.get("detected_at")),
            }
        )

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        severity_options = ["High", "Medium", "Low", "Undetermined"]

        if not df.empty:
            available_severities = sorted(
                set(df["Severity"].tolist()),
                key=lambda x: severity_options.index(x)
                if x in severity_options
                else len(severity_options),
            )
        else:
            available_severities = []

        severity_filter = st.multiselect(
            "Severity",
            severity_options,
            default=available_severities,
            key="severity_hist",
        )

    with col2:
        status_options = ["Processed", "Pending", "Failed", "Unknown"]

        if not df.empty:
            available_statuses = sorted(
                set(df["Status"].tolist()),
                key=lambda x: status_options.index(x)
                if x in status_options
                else len(status_options),
            )
        else:
            available_statuses = []

        status_filter = st.multiselect(
            "Status",
            status_options,
            default=available_statuses,
            key="status_hist",
        )

    with col3:
        sort_by = st.selectbox(
            "Sort By",
            [
                "Date (Newest)",
                "Date (Oldest)",
                "Confidence",
                "Pothole Count",
                "Severity",
            ],
        )

    # ------------------------------------------------------------------
    # Apply filters
    # ------------------------------------------------------------------

    df_filtered = df.copy()

    if not df_filtered.empty:

        if severity_filter:
            df_filtered = df_filtered[
                df_filtered["Severity"].isin(severity_filter)
            ]

        if status_filter:
            df_filtered = df_filtered[
                df_filtered["Status"].isin(status_filter)
            ]

        if sort_by == "Date (Newest)":
            df_filtered["_sort_date"] = pd.to_datetime(
                df_filtered["Date"],
                errors="coerce",
            )
            df_filtered = df_filtered.sort_values(
                "_sort_date",
                ascending=False,
            ).drop(columns=["_sort_date"])

        elif sort_by == "Date (Oldest)":
            df_filtered["_sort_date"] = pd.to_datetime(
                df_filtered["Date"],
                errors="coerce",
            )
            df_filtered = df_filtered.sort_values(
                "_sort_date",
                ascending=True,
            ).drop(columns=["_sort_date"])

        elif sort_by == "Confidence":
            df_filtered = df_filtered.sort_values(
                "Confidence",
                ascending=False,
            )

        elif sort_by == "Pothole Count":
            df_filtered = df_filtered.sort_values(
                "Potholes",
                ascending=False,
            )

        elif sort_by == "Severity":
            severity_order = {
                "High": 4,
                "Medium": 3,
                "Low": 2,
                "Undetermined": 1,
            }

            df_filtered["_severity_order"] = (
                df_filtered["Severity"].map(severity_order).fillna(0)
            )

            df_filtered = (
                df_filtered.sort_values(
                    "_severity_order",
                    ascending=False,
                )
                .drop(columns=["_severity_order"])
            )

    # ------------------------------------------------------------------
    # Pagination
    # ------------------------------------------------------------------

    items_per_page = st.selectbox(
        "Items per page",
        [10, 25, 50, 100],
        key="history_items_per_page",
    )

    total_records = len(df_filtered)

    if total_records == 0:
        st.info("No detection records match the selected filters.")
        return

    total_pages = (total_records + items_per_page - 1) // items_per_page

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown(f"**Total Records:** {total_records}")

    with col2:
        page = st.select_slider(
            "Page",
            options=list(range(1, total_pages + 1)),
            value=1,
            key="history_page",
        )

    with col3:
        st.markdown(f"**Page {page} of {total_pages}**")

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    df_page = df_filtered.iloc[start_idx:end_idx]

    # ------------------------------------------------------------------
    # Display records
    # ------------------------------------------------------------------

    for _, row in df_page.iterrows():

        with st.expander(
            f"{row['ID']} | {row['Location']} | "
            f"{row['Severity']} | {row['Date']}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Severity:** {row['Severity']}")
                st.write(f"**Status:** {row['Status']}")

            with col2:
                st.write(f"**Confidence:** {row['Confidence']:.2f}%")
                st.write(f"**Potholes Detected:** {row['Potholes']}")

            with col3:
                st.write(f"**Location:** {row['Location']}")
                st.write(f"**Date:** {row['Date']}")

            if st.button(
                f"Delete {row['ID']}",
                key=f"delete_{row['Detection ID']}",
            ):
                success, error = delete_detection(
                    row["Detection ID"],
                    token,
                )

                if success:
                    st.success(f"{row['ID']} deleted successfully.")
                    st.rerun()
                else:
                    st.error(f"Could not delete {row['ID']}: {error}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    st.markdown("## Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Filtered", len(df_filtered))

    with col2:
        avg_confidence = df_filtered["Confidence"].mean()
        st.metric(
            "Avg Confidence",
            f"{avg_confidence:.1f}%",
        )

    with col3:
        high_count = len(
            df_filtered[df_filtered["Severity"] == "High"]
        )
        st.metric("High Severity", high_count)

    with col4:
        total_potholes = int(df_filtered["Potholes"].sum())
        st.metric("Potholes Found", total_potholes)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    st.markdown("## Export")

    export_df = df_filtered[
        [
            "ID",
            "Location",
            "Severity",
            "Status",
            "Confidence",
            "Potholes",
            "Date",
        ]
    ].copy()

    col1, col2, col3 = st.columns(3)

    with col1:
        csv_data = export_df.to_csv(index=False)

        st.download_button(
            "Export as CSV",
            csv_data,
            file_name=f"detections_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        json_data = export_df.to_json(
            orient="records",
            indent=2,
        )

        st.download_button(
            "Export as JSON",
            json_data,
            file_name=f"detections_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col3:
        st.info("PDF export is handled by the backend report module.")
