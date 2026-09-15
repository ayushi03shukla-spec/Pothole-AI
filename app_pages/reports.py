import io
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:5000"


def get_token():
    """Get the current user's JWT token."""

    for key in (
        "token",
        "jwt_token",
        "access_token",
    ):
        token = st.session_state.get(key)

        if token:
            return token

    user = st.session_state.get("user")

    if isinstance(user, dict):
        for key in (
            "token",
            "jwt_token",
            "access_token",
        ):
            token = user.get(key)

            if token:
                return token

    return None


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def get_history(token):
    """Fetch the user's real detection history."""

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/history",
            headers=get_headers(token),
            params={
                "page": 1,
                "per_page": 1000,
            },
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        st.error(
            f"Could not load detection history: {exc}"
        )
        return None


def format_datetime(value):
    """Format an ISO datetime returned by Flask."""

    if not value:
        return "Unknown"

    try:
        dt = datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00",
            )
        )

        return dt.strftime(
            "%Y-%m-%d %H:%M"
        )

    except (
        ValueError,
        TypeError,
    ):
        return str(value)


def build_dataframe(detections):
    """Convert backend detection records to a DataFrame."""

    rows = []

    for detection in detections:

        confidence = detection.get(
            "confidence"
        )

        if confidence is None:
            confidence_percent = None
        else:
            confidence_percent = (
                float(confidence) * 100
            )

        severity = str(
            detection.get(
                "severity"
            )
            or "undetermined"
        ).capitalize()

        status = str(
            detection.get(
                "status"
            )
            or "unknown"
        ).capitalize()

        latitude = detection.get(
            "latitude"
        )

        longitude = detection.get(
            "longitude"
        )

        if (
            latitude is not None
            and longitude is not None
        ):
            location = (
                f"{float(latitude):.6f}, "
                f"{float(longitude):.6f}"
            )
        else:
            location = "Not available"

        rows.append(
            {
                "ID": (
                    f"D{detection.get('id', '')}"
                ),
                "Detection ID": detection.get(
                    "id"
                ),
                "Location": location,
                "Latitude": latitude,
                "Longitude": longitude,
                "Severity": severity,
                "Status": status,
                "Confidence": confidence_percent,
                "Potholes": int(
                    detection.get(
                        "pothole_count",
                        0,
                    )
                    or 0
                ),
                "Date": format_datetime(
                    detection.get(
                        "detected_at"
                    )
                ),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["_date_only"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    ).dt.date

    return df


def filter_by_date(
    df,
    date_range,
):
    """Filter real detection data by selected dates."""

    if df.empty or not date_range:
        return df.copy()

    filtered = df.copy()

    if isinstance(
        date_range,
        (list, tuple),
    ):

        if len(date_range) == 2:

            start_date = date_range[0]
            end_date = date_range[1]

            filtered = filtered[
                filtered["_date_only"].between(
                    start_date,
                    end_date,
                    inclusive="both",
                )
            ]

        elif len(date_range) == 1:

            filtered = filtered[
                filtered["_date_only"]
                == date_range[0]
            ]

    else:

        filtered = filtered[
            filtered["_date_only"]
            == date_range
        ]

    return filtered.copy()


def get_backend_report(
    endpoint,
    token,
):
    """Download CSV/PDF from the real Flask report API."""

    try:
        response = requests.get(
            f"{BACKEND_URL}{endpoint}",
            headers=get_headers(token),
            timeout=60,
        )

        response.raise_for_status()

        return response.content, None

    except requests.HTTPError as exc:

        response = exc.response

        if response is not None:

            try:
                error_data = response.json()

                message = (
                    error_data.get(
                        "error"
                    )
                    or str(error_data)
                )

            except ValueError:
                message = response.text

            return None, message

        return None, str(exc)

    except requests.RequestException as exc:
        return None, str(exc)


def make_excel(df):
    """Create an Excel file from filtered detection data."""

    export_df = df[
        [
            "ID",
            "Location",
            "Latitude",
            "Longitude",
            "Severity",
            "Status",
            "Confidence",
            "Potholes",
            "Date",
        ]
    ].copy()

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        export_df.to_excel(
            writer,
            index=False,
            sheet_name="Detections",
        )

    output.seek(0)

    return output.getvalue()


def show():
    """Display reports using real backend detection data."""

    st.markdown("# Reports")

    token = get_token()

    if not token:
        st.warning(
            "Please log in to use Reports."
        )
        return

    history_data = get_history(token)

    if history_data is None:
        return

    detections = history_data.get(
        "detections",
        [],
    )

    df = build_dataframe(
        detections
    )

    if df.empty:

        st.info(
            "No detection history is available "
            "to generate a report."
        )
        return

    tab_generate, tab_view = st.tabs(
        [
            "Generate",
            "Detection Data",
        ]
    )

    with tab_generate:
        show_generate_report(
            df,
            token,
        )

    with tab_view:
        show_detection_data(
            df,
        )


def show_generate_report(
    df,
    token,
):
    """Generate reports from real detection data."""

    st.markdown(
        "## Generate New Report"
    )

    col1, col2 = st.columns(2)

    with col1:

        report_title = st.text_input(
            "Report Title",
            placeholder=(
                "Example: Weekly Detection Summary"
            ),
            key="report_title",
        )

        report_type = st.selectbox(
            "Report Type",
            [
                "Summary",
                "Detailed",
                "Statistical Analysis",
                "Trend Analysis",
            ],
            key="report_type",
        )

        min_date = df[
            "_date_only"
        ].min()

        max_date = df[
            "_date_only"
        ].max()

        date_range = st.date_input(
            "Date Range",
            value=(
                min_date,
                max_date,
            ),
            key="report_date_range",
        )

        include_options = st.multiselect(
            "Include in Report",
            [
                "Statistics",
                "Charts",
                "Map Data",
                "Severity Analysis",
                "Trend Data",
            ],
            default=[
                "Statistics",
                "Charts",
                "Severity Analysis",
            ],
            key="report_include",
        )

    with col2:

        st.markdown(
            "### Report Settings"
        )

        format_type = st.radio(
            "Export Format",
            [
                "PDF",
                "CSV",
                "JSON",
                "Excel",
            ],
            key="report_format",
        )

        include_images = st.checkbox(
            "Include Detection Images",
            value=False,
            disabled=True,
            help=(
                "Image inclusion is not supported "
                "by the current backend report API."
            ),
        )

        include_map = st.checkbox(
            "Include Map Data",
            value=(
                "Map Data" in include_options
            ),
        )

        include_recommendations = st.checkbox(
            "Include Recommendations",
            value=False,
            disabled=True,
            help=(
                "Recommendations are not generated "
                "by the current backend report API."
            ),
        )

        st.markdown(
            "### Preview"
        )

        if isinstance(
            date_range,
            (list, tuple),
        ) and len(date_range) == 2:

            date_start = date_range[0]
            date_end = date_range[1]

        elif isinstance(
            date_range,
            (list, tuple),
        ) and len(date_range) == 1:

            date_start = date_range[0]
            date_end = date_range[0]

        else:

            date_start = date_range
            date_end = date_range

        st.info(
            f"""
**Report Summary**

Title: {report_title or "Untitled"}

Type: {report_type}

Date Range: {date_start} to {date_end}

Format: {format_type}

Records Available: {len(df)}
"""
        )

    # ------------------------------------------------------------
    # Generate
    # ------------------------------------------------------------

    if st.button(
        "Generate Report",
        use_container_width=True,
        key="generate_report_button",
    ):

        filtered_df = filter_by_date(
            df,
            date_range,
        )

        if filtered_df.empty:

            st.warning(
                "No detections exist in the selected "
                "date range."
            )

            return

        st.success(
            "Report data generated successfully."
        )

        st.markdown(
            "## Report Preview"
        )

        show_report_preview(
            filtered_df,
            report_title,
            report_type,
        )

        st.markdown(
            "## Download"
        )

        if format_type == "CSV":

            csv_data, error = (
                get_backend_report(
                    "/api/report/csv",
                    token,
                )
            )

            if error:

                st.error(
                    f"Could not generate CSV: {error}"
                )

            else:

                st.download_button(
                    "Download CSV",
                    csv_data,
                    file_name=(
                        f"{report_title or 'pothole_report'}_"
                        f"{datetime.now().strftime('%Y%m%d')}.csv"
                    ),
                    mime="text/csv",
                    use_container_width=True,
                )

                st.caption(
                    "The backend CSV export contains "
                    "the logged-in user's detection history."
                )

        elif format_type == "PDF":

            pdf_data, error = (
                get_backend_report(
                    "/api/report/pdf",
                    token,
                )
            )

            if error:

                st.error(
                    f"Could not generate PDF: {error}"
                )

            else:

                st.download_button(
                    "Download PDF",
                    pdf_data,
                    file_name=(
                        f"{report_title or 'pothole_report'}_"
                        f"{datetime.now().strftime('%Y%m%d')}.pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True,
                )

                st.caption(
                    "The backend PDF export contains "
                    "the logged-in user's detection history."
                )

        elif format_type == "JSON":

            json_df = filtered_df[
                [
                    "ID",
                    "Location",
                    "Latitude",
                    "Longitude",
                    "Severity",
                    "Status",
                    "Confidence",
                    "Potholes",
                    "Date",
                ]
            ].copy()

            json_df["Confidence"] = (
                json_df["Confidence"]
                .round(2)
            )

            json_data = json_df.to_json(
                orient="records",
                indent=2,
            )

            st.download_button(
                "Download JSON",
                json_data,
                file_name=(
                    f"{report_title or 'pothole_report'}_"
                    f"{datetime.now().strftime('%Y%m%d')}.json"
                ),
                mime="application/json",
                use_container_width=True,
            )

        elif format_type == "Excel":

            excel_data = make_excel(
                filtered_df
            )

            st.download_button(
                "Download Excel",
                excel_data,
                file_name=(
                    f"{report_title or 'pothole_report'}_"
                    f"{datetime.now().strftime('%Y%m%d')}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True,
            )


def show_report_preview(
    df,
    title,
    report_type,
):
    """Display a preview based on actual detection records."""

    st.markdown(
        f"### {title or 'Report'}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "#### Key Metrics"
        )

        total_scans = len(df)

        total_potholes = int(
            df["Potholes"].sum()
        )

        valid_confidence = (
            df["Confidence"]
            .dropna()
        )

        if not valid_confidence.empty:

            avg_confidence = float(
                valid_confidence.mean()
            )

        else:

            avg_confidence = 0.0

        high_count = len(
            df[
                df["Severity"]
                == "High"
            ]
        )

        metric_col1, metric_col2 = (
            st.columns(2)
        )

        with metric_col1:

            st.metric(
                "Total Scans",
                total_scans,
            )

            st.metric(
                "Potholes Found",
                total_potholes,
            )

        with metric_col2:

            st.metric(
                "Avg Confidence",
                f"{avg_confidence:.1f}%",
            )

            st.metric(
                "High Severity",
                high_count,
            )

    with col2:

        st.markdown(
            "#### Detection Trend"
        )

        trend_df = df.copy()

        trend_df["Date Only"] = pd.to_datetime(
            trend_df["_date_only"],
            errors="coerce",
        )

        daily_counts = (
            trend_df
            .dropna(subset=["Date Only"])
            .groupby("Date Only")
            .size()
            .reset_index(
                name="Detections"
            )
        )

        if not daily_counts.empty:

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=daily_counts[
                        "Date Only"
                    ],
                    y=daily_counts[
                        "Detections"
                    ],
                    mode="lines+markers",
                )
            )

            fig.update_layout(
                height=300,
                margin=dict(
                    l=0,
                    r=0,
                    t=30,
                    b=0,
                ),
                xaxis_title="Date",
                yaxis_title=(
                    "Detection Scans"
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.info(
                "No dated detections available "
                "for the trend chart."
            )

    # ------------------------------------------------------------
    # Severity distribution
    # ------------------------------------------------------------

    st.markdown(
        "#### Severity Distribution"
    )

    severity_order = [
        "High",
        "Medium",
        "Low",
        "Undetermined",
    ]

    severity_counts = []

    for severity in severity_order:

        severity_counts.append(
            len(
                df[
                    df["Severity"]
                    == severity
                ]
            )
        )

    fig_severity = go.Figure(
        data=[
            go.Bar(
                x=severity_order,
                y=severity_counts,
            )
        ]
    )

    fig_severity.update_layout(
        height=300,
        xaxis_title="Severity",
        yaxis_title=(
            "Number of Detections"
        ),
    )

    st.plotly_chart(
        fig_severity,
        use_container_width=True,
    )


def show_detection_data(df):
    """Show the actual detection records used for reports."""

    st.markdown(
        "## Detection Data"
    )

    display_df = df[
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

    display_df["Confidence"] = (
        display_df["Confidence"]
        .apply(
            lambda value: (
                f"{float(value):.2f}%"
                if pd.notna(value)
                else "N/A"
            )
        )
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "These are the real detection records "
        "currently stored for the logged-in user."
    )
