import math
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
import folium

from folium.plugins import HeatMap
from streamlit_folium import st_folium


BACKEND_URL = "http://127.0.0.1:5000"

NOMINATIM_URL = (
    "https://nominatim.openstreetmap.org/search"
)

NOMINATIM_USER_AGENT = (
    "PotholeAI/1.0 "
    "(road-damage-detection-project)"
)


def get_history(token):
    """Get detection history from Flask backend."""

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/history",
            headers={
                "Authorization": f"Bearer {token}"
            },
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


def geocode_locality(query):
    """Convert locality/address into latitude and longitude."""

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "jsonv2",
                "limit": 1,
            },
            headers={
                "User-Agent": NOMINATIM_USER_AGENT
            },
            timeout=15,
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            return None

        result = results[0]

        return {
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
            "display_name": result.get(
                "display_name",
                query,
            ),
        }

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
    ):
        return None


def haversine_distance_km(
    lat1,
    lon1,
    lat2,
    lon2,
):
    """Calculate distance between two coordinates."""

    earth_radius_km = 6371.0

    lat1 = math.radians(float(lat1))
    lat2 = math.radians(float(lat2))

    delta_lat = math.radians(
        float(lat2) - float(lat1)
    )

    delta_lon = math.radians(
        float(lon2) - float(lon1)
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = (
        2
        * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )
    )

    return earth_radius_km * c


def format_datetime(value):
    """Format backend datetime for display."""

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
    """Convert API detections into a DataFrame."""

    rows = []

    for detection in detections:

        confidence = detection.get(
            "confidence"
        )

        if confidence is None:
            confidence_percent = 0.0
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

        detected_at = detection.get(
            "detected_at"
        )

        rows.append(
            {
                "id": detection.get("id"),
                "Detection": (
                    f"D{detection.get('id', '')}"
                ),
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
                "Latitude": detection.get(
                    "latitude"
                ),
                "Longitude": detection.get(
                    "longitude"
                ),
                "Date": format_datetime(
                    detected_at
                ),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Create the date column once.
    # All filtering uses this column.
    df["_date_only"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    ).dt.date

    return df


def show():
    """Display the real pothole map."""

    st.markdown(
        "# Pothole Locations Map"
    )

    token = st.session_state.get(
        "token"
    )

    if not token:
        st.warning(
            "Please log in to view the map."
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
            "No detection records are available yet."
        )
        return

    # ------------------------------------------------------------
    # Locality search
    # ------------------------------------------------------------

    st.markdown(
        "## Search Potholes by Locality"
    )

    search_col1, search_col2 = (
        st.columns([3, 1])
    )

    with search_col1:

        locality_query = st.text_input(
            "Enter locality, area, city or address",
            placeholder=(
                "Example: Sigra, Varanasi"
            ),
            key="locality_search",
        )

    with search_col2:

        search_radius = st.slider(
            "Radius (km)",
            min_value=1,
            max_value=25,
            value=5,
            step=1,
            key="locality_radius",
        )

    if st.button(
        "Search Locality",
        key="search_locality_button",
        use_container_width=False,
    ):

        if not locality_query.strip():

            st.warning(
                "Please enter a locality."
            )

        else:

            with st.spinner(
                "Finding locality..."
            ):

                locality = geocode_locality(
                    locality_query.strip()
                )

            if locality is None:

                st.error(
                    "Locality not found. "
                    "Try including city and state."
                )

                st.session_state.pop(
                    "searched_locality",
                    None,
                )

            else:

                st.session_state[
                    "searched_locality"
                ] = locality

                st.success(
                    "Locality found: "
                    f"{locality['display_name']}"
                )

    searched_locality = st.session_state.get(
        "searched_locality"
    )

    # ------------------------------------------------------------
    # Sidebar filters
    # ------------------------------------------------------------

    st.sidebar.markdown(
        "### Filters"
    )

    severity_options = [
        "High",
        "Medium",
        "Low",
        "Undetermined",
    ]

    status_options = [
        "Processed",
        "Pending",
        "Failed",
        "Unknown",
    ]

    current_severities = [
        value
        for value in severity_options
        if value in df["Severity"].unique()
    ]

    current_statuses = [
        value
        for value in status_options
        if value in df["Status"].unique()
    ]

    severity_filter = st.sidebar.multiselect(
        "Severity",
        severity_options,
        default=current_severities,
        key="map_severity_filter",
    )

    status_filter = st.sidebar.multiselect(
        "Status",
        status_options,
        default=current_statuses,
        key="map_status_filter",
    )

    # ------------------------------------------------------------
    # Date filter
    # ------------------------------------------------------------

    valid_dates = (
        df["_date_only"].dropna()
    )

    date_range = None

    if not valid_dates.empty:

        min_date = valid_dates.min()
        max_date = valid_dates.max()

        date_range = st.sidebar.date_input(
            "Date Range",
            value=(
                min_date,
                max_date,
            ),
            key="map_date_filter",
        )

    # ------------------------------------------------------------
    # Create filtered dataframe
    # ------------------------------------------------------------

    filtered_df = df.copy()

    if severity_filter:

        filtered_df = filtered_df[
            filtered_df["Severity"].isin(
                severity_filter
            )
        ].copy()

    if status_filter:

        filtered_df = filtered_df[
            filtered_df["Status"].isin(
                status_filter
            )
        ].copy()

    # Date filtering uses the column that already exists.
    if date_range:

        if isinstance(
            date_range,
            (list, tuple),
        ):

            if len(date_range) == 2:

                start_date = date_range[0]
                end_date = date_range[1]

                filtered_df = filtered_df[
                    filtered_df[
                        "_date_only"
                    ].between(
                        start_date,
                        end_date,
                        inclusive="both",
                    )
                ].copy()

            elif len(date_range) == 1:

                filtered_df = filtered_df[
                    filtered_df[
                        "_date_only"
                    ]
                    == date_range[0]
                ].copy()

        else:

            filtered_df = filtered_df[
                filtered_df[
                    "_date_only"
                ]
                == date_range
            ].copy()

    # ------------------------------------------------------------
    # Locality radius filtering
    # ------------------------------------------------------------

    if searched_locality:

        search_lat = float(
            searched_locality[
                "latitude"
            ]
        )

        search_lon = float(
            searched_locality[
                "longitude"
            ]
        )

        distances = []

        for _, row in filtered_df.iterrows():

            latitude = row["Latitude"]
            longitude = row["Longitude"]

            if (
                pd.isna(latitude)
                or pd.isna(longitude)
            ):

                distances.append(
                    None
                )

            else:

                distances.append(
                    haversine_distance_km(
                        search_lat,
                        search_lon,
                        float(latitude),
                        float(longitude),
                    )
                )

        filtered_df[
            "Distance (km)"
        ] = distances

        filtered_df = filtered_df[
            filtered_df[
                "Distance (km)"
            ].notna()
        ].copy()

        filtered_df = filtered_df[
            filtered_df[
                "Distance (km)"
            ]
            <= search_radius
        ].copy()

    # ------------------------------------------------------------
    # GPS-only dataframe
    # ------------------------------------------------------------

    mapped_df = filtered_df[
        filtered_df["Latitude"].notna()
        & filtered_df["Longitude"].notna()
    ].copy()

    # ------------------------------------------------------------
    # Search result message
    # ------------------------------------------------------------

    if searched_locality:

        st.info(
            f"{len(mapped_df)} mapped detection(s) "
            f"found within {search_radius} km of "
            f"{searched_locality['display_name']}."
        )

    # ------------------------------------------------------------
    # Detection Map
    # ------------------------------------------------------------

    st.markdown(
        "## Detection Map"
    )

    if mapped_df.empty:

        st.warning(
            "No matching detections have GPS "
            "coordinates."
        )

    else:

        center_lat = float(
            mapped_df[
                "Latitude"
            ].mean()
        )

        center_lon = float(
            mapped_df[
                "Longitude"
            ].mean()
        )

        if searched_locality:

            center_lat = float(
                searched_locality[
                    "latitude"
                ]
            )

            center_lon = float(
                searched_locality[
                    "longitude"
                ]
            )

        map_obj = folium.Map(
            location=[
                center_lat,
                center_lon,
            ],
            zoom_start=14,
            tiles="OpenStreetMap",
        )

        # Searched locality marker.
        if searched_locality:

            folium.Marker(
                location=[
                    float(
                        searched_locality[
                            "latitude"
                        ]
                    ),
                    float(
                        searched_locality[
                            "longitude"
                        ]
                    ),
                ],
                tooltip=(
                    "Searched locality"
                ),
                popup=(
                    searched_locality[
                        "display_name"
                    ]
                ),
                icon=folium.Icon(
                    color="black",
                    icon="search",
                ),
            ).add_to(
                map_obj
            )

            folium.Circle(
                location=[
                    float(
                        searched_locality[
                            "latitude"
                        ]
                    ),
                    float(
                        searched_locality[
                            "longitude"
                        ]
                    ),
                ],
                radius=(
                    search_radius * 1000
                ),
                color="blue",
                fill=False,
                weight=2,
            ).add_to(
                map_obj
            )

        severity_colors = {
            "High": "red",
            "Medium": "orange",
            "Low": "green",
            "Undetermined": "blue",
        }

        for _, row in mapped_df.iterrows():

            severity = row[
                "Severity"
            ]

            marker_color = severity_colors.get(
                severity,
                "blue",
            )

            distance_text = ""

            if (
                searched_locality
                and "Distance (km)"
                in row.index
                and pd.notna(
                    row[
                        "Distance (km)"
                    ]
                )
            ):

                distance_text = (
                    f"Distance: "
                    f"{float(row['Distance (km)']):.2f} km<br>"
                )

            popup_html = f"""
            <div style="font-size:14px;">
                <b>{row['Detection']}</b><br>
                Severity: {severity}<br>
                Status: {row['Status']}<br>
                Confidence: {row['Confidence']:.2f}%<br>
                Potholes: {row['Potholes']}<br>
                Date: {row['Date']}<br>
                {distance_text}
                Location:
                ({float(row['Latitude']):.6f},
                {float(row['Longitude']):.6f})
            </div>
            """

            folium.CircleMarker(
                location=[
                    float(row["Latitude"]),
                    float(row["Longitude"]),
                ],
                radius=9,
                popup=folium.Popup(
                    popup_html,
                    max_width=320,
                ),
                tooltip=(
                    f"{row['Detection']} | "
                    f"{severity} | "
                    f"{row['Confidence']:.1f}%"
                ),
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.75,
                weight=2,
            ).add_to(
                map_obj
            )

        st_folium(
            map_obj,
            width=1400,
            height=600,
        )

    # ------------------------------------------------------------
    # Map statistics
    # ------------------------------------------------------------

    st.markdown(
        "## Map Statistics"
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "Detection Scans",
            len(filtered_df),
        )

    with col2:

        st.metric(
            "Mapped Scans",
            len(mapped_df),
        )

    with col3:

        st.metric(
            "Potholes Found",
            int(
                filtered_df[
                    "Potholes"
                ].sum()
            ),
        )

    with col4:

        average_confidence = (
            float(
                filtered_df[
                    "Confidence"
                ].mean()
            )
            if not filtered_df.empty
            else 0.0
        )

        st.metric(
            "Avg Confidence",
            f"{average_confidence:.1f}%",
        )

    # ------------------------------------------------------------
    # Detection details
    # ------------------------------------------------------------

    st.markdown(
        "## Detection Details"
    )

    display_columns = [
        "Detection",
        "Severity",
        "Status",
        "Confidence",
        "Potholes",
        "Latitude",
        "Longitude",
        "Date",
    ]

    if (
        searched_locality
        and "Distance (km)"
        in filtered_df.columns
    ):

        display_columns.append(
            "Distance (km)"
        )

    display_df = filtered_df[
        display_columns
    ].copy()

    display_df[
        "Confidence"
    ] = display_df[
        "Confidence"
    ].apply(
        lambda value: (
            f"{float(value):.2f}%"
        )
    )

    display_df[
        "Latitude"
    ] = display_df[
        "Latitude"
    ].apply(
        lambda value: (
            round(
                float(value),
                6,
            )
            if pd.notna(value)
            else None
        )
    )

    display_df[
        "Longitude"
    ] = display_df[
        "Longitude"
    ].apply(
        lambda value: (
            round(
                float(value),
                6,
            )
            if pd.notna(value)
            else None
        )
    )

    if "Distance (km)" in display_df.columns:

        display_df[
            "Distance (km)"
        ] = display_df[
            "Distance (km)"
        ].apply(
            lambda value: (
                f"{float(value):.2f}"
                if pd.notna(value)
                else None
            )
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------------
    # Heatmap
    # ------------------------------------------------------------

    st.markdown(
        "## Density Heatmap"
    )

    if mapped_df.empty:

        st.info(
            "Heatmap is unavailable because "
            "there are no GPS-tagged detections."
        )

    else:

        heat_lat = float(
            mapped_df[
                "Latitude"
            ].mean()
        )

        heat_lon = float(
            mapped_df[
                "Longitude"
            ].mean()
        )

        if searched_locality:

            heat_lat = float(
                searched_locality[
                    "latitude"
                ]
            )

            heat_lon = float(
                searched_locality[
                    "longitude"
                ]
            )

        heat_map = folium.Map(
            location=[
                heat_lat,
                heat_lon,
            ],
            zoom_start=14,
            tiles="OpenStreetMap",
        )

        heat_data = []

        for _, row in mapped_df.iterrows():

            heat_data.append(
                [
                    float(
                        row["Latitude"]
                    ),
                    float(
                        row["Longitude"]
                    ),
                    max(
                        float(
                            row["Confidence"]
                        )
                        / 100,
                        0.01,
                    ),
                ]
            )

        HeatMap(
            heat_data,
            radius=20,
            blur=15,
            min_opacity=0.4,
        ).add_to(
            heat_map
        )

        st_folium(
            heat_map,
            width=1400,
            height=500,
        )

    # ------------------------------------------------------------
    # Export
    # ------------------------------------------------------------

    st.markdown(
        "## Export Options"
    )

    export_columns = [
        "id",
        "Detection",
        "Severity",
        "Status",
        "Confidence",
        "Potholes",
        "Latitude",
        "Longitude",
        "Date",
    ]

    if (
        searched_locality
        and "Distance (km)"
        in filtered_df.columns
    ):

        export_columns.append(
            "Distance (km)"
        )

    export_df = filtered_df[
        export_columns
    ].copy()

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.download_button(
            "Export as CSV",
            export_df.to_csv(
                index=False
            ),
            file_name=(
                "pothole_detections.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

    with col2:

        st.download_button(
            "Export as JSON",
            export_df.to_json(
                orient="records",
                indent=2,
            ),
            file_name=(
                "pothole_detections.json"
            ),
            mime="application/json",
            use_container_width=True,
        )

    with col3:

        if mapped_df.empty:

            st.info(
                "No GPS data available "
                "to export a map."
            )

        else:

            export_map = folium.Map(
                location=[
                    float(
                        mapped_df[
                            "Latitude"
                        ].mean()
                    ),
                    float(
                        mapped_df[
                            "Longitude"
                        ].mean()
                    ),
                ],
                zoom_start=14,
                tiles="OpenStreetMap",
            )

            for _, row in mapped_df.iterrows():

                folium.Marker(
                    location=[
                        float(
                            row["Latitude"]
                        ),
                        float(
                            row["Longitude"]
                        ),
                    ],
                    popup=(
                        f"{row['Detection']} | "
                        f"{row['Severity']} | "
                        f"{row['Confidence']:.2f}%"
                    ),
                ).add_to(
                    export_map
                )

            st.download_button(
                "Export Map HTML",
                export_map
                .get_root()
                .render(),
                file_name=(
                    "pothole_map.html"
                ),
                mime="text/html",
                use_container_width=True,
            )
