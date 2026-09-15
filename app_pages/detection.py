import io

import piexif
import requests
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import plotly.graph_objects as go


BACKEND_URL = "http://127.0.0.1:5000"


def show():
    """Display the detection page."""

    st.markdown("# Pothole Detection")
    st.markdown(
        "Upload images or videos for AI-powered pothole detection"
    )

    tab_image, tab_video, tab_camera = st.tabs(
        ["Image", "Video", "Camera"]
    )

    with tab_image:
        show_image_detection()

    with tab_video:
        show_video_detection()

    with tab_camera:
        show_camera_detection()


def get_api_token():
    """Get JWT token from Streamlit session state."""

    for key in ("token", "jwt_token", "access_token"):
        value = st.session_state.get(key)

        if value:
            return value

    user = st.session_state.get("user")

    if isinstance(user, dict):
        for key in ("token", "jwt_token", "access_token"):
            value = user.get(key)

            if value:
                return value

    return None


def rational_to_float(value):
    """Convert an EXIF rational value to float."""

    return float(value[0]) / float(value[1])


def convert_dms_to_decimal(dms, reference):
    """Convert EXIF degrees/minutes/seconds to decimal degrees."""

    degrees = rational_to_float(dms[0])
    minutes = rational_to_float(dms[1])
    seconds = rational_to_float(dms[2])

    decimal = (
        degrees
        + minutes / 60.0
        + seconds / 3600.0
    )

    if isinstance(reference, bytes):
        reference = reference.decode(
            "utf-8",
            errors="ignore",
        )

    if reference in ("S", "W"):
        decimal = -decimal

    return decimal


def extract_gps_from_exif(uploaded_file):
    """
    Extract latitude and longitude from image EXIF GPS metadata.

    Returns:
        tuple(latitude, longitude)
        or (None, None) when GPS metadata is unavailable.
    """

    try:
        image_bytes = uploaded_file.getvalue()

        if not image_bytes:
            return None, None

        exif_data = piexif.load(image_bytes)

        gps_data = exif_data.get("GPS", {})

        if not gps_data:
            return None, None

        latitude = gps_data.get(
            piexif.GPSIFD.GPSLatitude
        )

        latitude_reference = gps_data.get(
            piexif.GPSIFD.GPSLatitudeRef
        )

        longitude = gps_data.get(
            piexif.GPSIFD.GPSLongitude
        )

        longitude_reference = gps_data.get(
            piexif.GPSIFD.GPSLongitudeRef
        )

        if not all(
            [
                latitude,
                latitude_reference,
                longitude,
                longitude_reference,
            ]
        ):
            return None, None

        latitude_decimal = convert_dms_to_decimal(
            latitude,
            latitude_reference,
        )

        longitude_decimal = convert_dms_to_decimal(
            longitude,
            longitude_reference,
        )

        return (
            latitude_decimal,
            longitude_decimal,
        )

    except Exception:
        return None, None


def draw_detection_boxes(image, potholes):
    """Draw real YOLO bounding boxes returned by Flask."""

    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for index, pothole in enumerate(potholes):

        bbox = pothole.get("bbox", {})

        x_min = int(
            float(
                bbox.get("x_min", 0)
            )
        )

        y_min = int(
            float(
                bbox.get("y_min", 0)
            )
        )

        x_max = int(
            float(
                bbox.get("x_max", 0)
            )
        )

        y_max = int(
            float(
                bbox.get("y_max", 0)
            )
        )

        confidence = float(
            pothole.get(
                "confidence",
                0.0,
            )
        )

        severity = str(
            pothole.get(
                "severity",
                "undetermined",
            )
        ).capitalize()

        label = (
            f"P{index + 1:03d} | "
            f"{severity} | "
            f"{confidence * 100:.1f}%"
        )

        draw.rectangle(
            [
                x_min,
                y_min,
                x_max,
                y_max,
            ],
            outline="red",
            width=4,
        )

        if font is not None:

            text_bbox = draw.textbbox(
                (
                    x_min,
                    y_min,
                ),
                label,
                font=font,
            )

            text_width = (
                text_bbox[2]
                - text_bbox[0]
            )

            text_height = (
                text_bbox[3]
                - text_bbox[1]
            )

        else:

            text_width = (
                len(label) * 7
            )

            text_height = 12

        label_y = max(
            0,
            y_min - text_height - 6,
        )

        draw.rectangle(
            [
                x_min,
                label_y,
                x_min
                + text_width
                + 8,
                label_y
                + text_height
                + 6,
            ],
            fill="red",
        )

        draw.text(
            (
                x_min + 4,
                label_y + 3,
            ),
            label,
            fill="white",
            font=font,
        )

    return annotated


def upload_image_to_backend(
    uploaded_file,
    token,
    latitude=None,
    longitude=None,
):
    """Upload image and optional GPS coordinates to Flask."""

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
            or "application/octet-stream",
        )
    }

    data = {}

    if latitude is not None:
        data["latitude"] = str(
            latitude
        )

    if longitude is not None:
        data["longitude"] = str(
            longitude
        )

    response = requests.post(
        f"{BACKEND_URL}/api/upload/image",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        files=files,
        data=data,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def run_backend_detection(
    detection_id,
    token,
    confidence=0.50,
):
    """Trigger YOLO detection through Flask."""

    response = requests.post(
        f"{BACKEND_URL}/api/detect/{detection_id}",
        headers={
            "Authorization": (
                f"Bearer {token}"
            )
        },
        params={
            "confidence": confidence
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()


def show_image_detection():
    """Handle image detection through the Flask backend."""

    st.markdown("## Image Upload")

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "bmp",
        ],
        help="Upload an image for pothole detection",
        key="backend_image_upload",
    )

    if uploaded_file is None:
        return

    # ------------------------------------------------------------
    # Extract EXIF GPS automatically
    # ------------------------------------------------------------

    exif_latitude, exif_longitude = (
        extract_gps_from_exif(
            uploaded_file
        )
    )

    image = Image.open(
        uploaded_file
    ).convert("RGB")

    st.image(
        image,
        caption="Original Image",
        use_container_width=True,
    )

    file_size = (
        uploaded_file.size
        / (1024 * 1024)
    )

    st.info(
        f"File size: {file_size:.2f} MB"
    )

    # ------------------------------------------------------------
    # Location
    # ------------------------------------------------------------

    st.markdown(
        "### Detection Location"
    )

    if (
        exif_latitude is not None
        and exif_longitude is not None
    ):

        st.success(
            "GPS location found automatically "
            "from image metadata."
        )

        st.caption(
            f"Detected location: "
            f"{exif_latitude:.6f}, "
            f"{exif_longitude:.6f}"
        )

        use_exif_location = st.checkbox(
            "Use detected GPS location",
            value=True,
            key="use_exif_location",
        )

    else:

        st.info(
            "No GPS metadata was found "
            "in this image."
        )

        use_exif_location = False

    location_enabled = st.checkbox(
        "Add GPS location",
        value=(
            exif_latitude is not None
            and exif_longitude is not None
        ),
        help=(
            "Use GPS metadata from the image "
            "or enter the location manually."
        ),
        key="image_location_enabled",
    )

    latitude = None
    longitude = None

    if location_enabled:

        if (
            use_exif_location
            and exif_latitude is not None
            and exif_longitude is not None
        ):

            latitude = exif_latitude
            longitude = exif_longitude

            st.caption(
                "Using GPS coordinates "
                "from the image."
            )

        else:

            location_col1, location_col2 = (
                st.columns(2)
            )

            with location_col1:

                latitude = st.number_input(
                    "Latitude",
                    min_value=-90.0,
                    max_value=90.0,
                    value=0.0,
                    format="%.6f",
                    help=(
                        "Latitude must be between "
                        "-90 and 90."
                    ),
                    key="image_latitude",
                )

            with location_col2:

                longitude = st.number_input(
                    "Longitude",
                    min_value=-180.0,
                    max_value=180.0,
                    value=0.0,
                    format="%.6f",
                    help=(
                        "Longitude must be between "
                        "-180 and 180."
                    ),
                    key="image_longitude",
                )

    # ------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------

    confidence_threshold = st.slider(
        "Detection Confidence Threshold",
        min_value=0.25,
        max_value=0.90,
        value=0.50,
        step=0.05,
        help=(
            "Detections below this confidence "
            "are ignored."
        ),
        key="image_confidence_threshold",
    )

    # ------------------------------------------------------------
    # Analyze
    # ------------------------------------------------------------

    if st.button(
        "Analyze Image",
        use_container_width=True,
        key="backend_analyze_image",
    ):

        token = get_api_token()

        if not token:

            st.error(
                "Authentication token not found. "
                "Please log in again before "
                "analyzing an image."
            )

            return

        if location_enabled:

            if (
                latitude is None
                or longitude is None
            ):

                st.error(
                    "Please provide valid GPS "
                    "coordinates or turn off "
                    "Add GPS location."
                )

                return

            if (
                float(latitude) == 0.0
                and float(longitude) == 0.0
            ):

                st.error(
                    "Please enter a real GPS "
                    "location. Latitude and "
                    "longitude cannot both be 0."
                )

                return

        try:

            with st.spinner(
                "Uploading image to backend..."
            ):

                upload_result = (
                    upload_image_to_backend(
                        uploaded_file,
                        token,
                        latitude=(
                            latitude
                            if location_enabled
                            else None
                        ),
                        longitude=(
                            longitude
                            if location_enabled
                            else None
                        ),
                    )
                )

            detection = upload_result.get(
                "detection"
            )

            if not detection:

                st.error(
                    "Backend did not return "
                    "a detection record."
                )

                return

            detection_id = detection[
                "id"
            ]

            st.info(
                "Image uploaded successfully. "
                f"Detection ID: {detection_id}"
            )

            with st.spinner(
                "Running YOLOv8 detection..."
            ):

                detection_result = (
                    run_backend_detection(
                        detection_id,
                        token,
                        confidence_threshold,
                    )
                )

            detection = detection_result.get(
                "detection"
            )

            if not detection:

                st.error(
                    "Backend did not return "
                    "detection results."
                )

                return

            st.success(
                "Analysis Complete!"
            )

            potholes = detection.get(
                "potholes",
                [],
            )

            # ----------------------------------------------------
            # Results
            # ----------------------------------------------------

            result_col1, result_col2 = (
                st.columns(2)
            )

            with result_col1:

                st.markdown(
                    "### Detection Result"
                )

                annotated_image = (
                    draw_detection_boxes(
                        image,
                        potholes,
                    )
                )

                st.image(
                    annotated_image,
                    caption=(
                        "YOLOv8 Detection Result"
                    ),
                    use_container_width=True,
                )

            with result_col2:

                pothole_count = int(
                    detection.get(
                        "pothole_count",
                        0,
                    )
                    or 0
                )

                average_confidence = float(
                    detection.get(
                        "confidence",
                        0.0,
                    )
                    or 0.0
                )

                overall_severity = str(
                    detection.get(
                        "severity",
                        "none",
                    )
                    or "none"
                )

                status = str(
                    detection.get(
                        "status",
                        "unknown",
                    )
                )

                st.metric(
                    "Total Potholes",
                    pothole_count,
                )

                st.metric(
                    "Average Confidence",
                    (
                        f"{average_confidence * 100:.2f}%"
                    ),
                )

                st.metric(
                    "Severity",
                    overall_severity.capitalize(),
                )

                if (
                    overall_severity.lower()
                    == "undetermined"
                ):

                    st.info(
                        "Severity cannot be reliably "
                        "determined from this image "
                        "alone. Physical depth or scale "
                        "information is required for "
                        "real-world severity classification."
                    )

                st.caption(
                    f"Backend status: {status}"
                )

                st.caption(
                    "Confidence threshold used: "
                    f"{confidence_threshold:.0%}"
                )

                if location_enabled:

                    st.caption(
                        "GPS saved: "
                        f"{float(latitude):.6f}, "
                        f"{float(longitude):.6f}"
                    )

                else:

                    st.caption(
                        "GPS: Not provided"
                    )

            # ----------------------------------------------------
            # Summary table
            # ----------------------------------------------------

            st.markdown(
                "### Detection Summary"
            )

            severity_counts = {
                "High": 0,
                "Medium": 0,
                "Low": 0,
                "Undetermined": 0,
            }

            detected = []

            image_width, image_height = (
                image.size
            )

            image_area = (
                image_width
                * image_height
            )

            for index, pothole in enumerate(
                potholes
            ):

                confidence = float(
                    pothole.get(
                        "confidence",
                        0.0,
                    )
                )

                width = float(
                    pothole.get(
                        "width",
                        0.0,
                    )
                )

                height = float(
                    pothole.get(
                        "height",
                        0.0,
                    )
                )

                size = float(
                    pothole.get(
                        "size",
                        width * height,
                    )
                )

                severity = str(
                    pothole.get(
                        "severity",
                        "undetermined",
                    )
                ).capitalize()

                if severity not in severity_counts:
                    severity = "Undetermined"

                severity_counts[
                    severity
                ] += 1

                bbox = pothole.get(
                    "bbox",
                    {},
                )

                x_min = float(
                    bbox.get(
                        "x_min",
                        0,
                    )
                )

                y_min = float(
                    bbox.get(
                        "y_min",
                        0,
                    )
                )

                x_max = float(
                    bbox.get(
                        "x_max",
                        0,
                    )
                )

                y_max = float(
                    bbox.get(
                        "y_max",
                        0,
                    )
                )

                center_x = int(
                    (
                        x_min
                        + x_max
                    )
                    / 2
                )

                center_y = int(
                    (
                        y_min
                        + y_max
                    )
                    / 2
                )

                area_ratio = (
                    size / image_area
                    if image_area > 0
                    else 0
                )

                detected.append(
                    {
                        "ID": (
                            f"P{index + 1:03d}"
                        ),
                        "Severity": severity,
                        "Confidence": (
                            confidence * 100
                        ),
                        "Size": (
                            f"{width:.0f} x "
                            f"{height:.0f}"
                        ),
                        "Location": (
                            f"({center_x}, "
                            f"{center_y})"
                        ),
                        "Area Ratio": (
                            f"{area_ratio:.2%}"
                        ),
                    }
                )

            if detected:

                df = pd.DataFrame(
                    detected
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No potholes were detected."
                )

            # ----------------------------------------------------
            # Severity chart
            # ----------------------------------------------------

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=[
                            "High",
                            "Medium",
                            "Low",
                            "Undetermined",
                        ],
                        y=[
                            severity_counts[
                                "High"
                            ],
                            severity_counts[
                                "Medium"
                            ],
                            severity_counts[
                                "Low"
                            ],
                            severity_counts[
                                "Undetermined"
                            ],
                        ],
                    )
                ]
            )

            fig.update_layout(
                title=(
                    "Severity Distribution"
                ),
                height=300,
                yaxis_title=(
                    "Number of Potholes"
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            # ----------------------------------------------------
            # Individual pothole details
            # ----------------------------------------------------

            st.markdown(
                "### Detected Potholes"
            )

            for pothole in detected:

                with st.expander(
                    f"{pothole['ID']} - "
                    f"{pothole['Severity']}"
                ):

                    detail_col1, detail_col2 = (
                        st.columns(2)
                    )

                    with detail_col1:

                        st.write(
                            "**Confidence:** "
                            f"{pothole['Confidence']:.2f}%"
                        )

                        st.write(
                            "**Bounding Box Size:** "
                            f"{pothole['Size']}"
                        )

                    with detail_col2:

                        st.write(
                            "**Center:** "
                            f"{pothole['Location']}"
                        )

                        st.write(
                            "**Area Ratio:** "
                            f"{pothole['Area Ratio']}"
                        )

        except requests.HTTPError as exc:

            response = exc.response

            if response is not None:

                try:

                    error_data = (
                        response.json()
                    )

                    message = (
                        error_data.get(
                            "error"
                        )
                        or error_data.get(
                            "msg"
                        )
                        or str(error_data)
                    )

                    st.error(
                        f"Backend error: {message}"
                    )

                except ValueError:

                    st.error(
                        "Backend returned HTTP "
                        f"{response.status_code}: "
                        f"{response.text}"
                    )

            else:

                st.error(
                    f"Backend request failed: "
                    f"{exc}"
                )

        except requests.RequestException as exc:

            st.error(
                "Could not connect to Flask "
                f"backend at {BACKEND_URL}. "
                "Make sure Flask is running. "
                f"Details: {exc}"
            )

        except Exception as exc:

            st.exception(exc)


def show_video_detection():
    """Handle video detection."""

    st.markdown("## Video Upload")

    uploaded_video = st.file_uploader(
        "Choose a video",
        type=[
            "mp4",
            "avi",
            "mov",
            "mkv",
        ],
        help="Upload a video for pothole detection",
    )

    if uploaded_video is None:
        return

    st.video(uploaded_video)

    file_size = (
        uploaded_video.size
        / (1024 * 1024)
    )

    st.info(
        f"File size: {file_size:.2f} MB"
    )

    st.warning(
        "Video detection is not connected "
        "to the real YOLO backend yet."
    )


def show_camera_detection():
    """Handle camera image detection."""

    st.markdown(
        "## Real-Time Detection"
    )

    picture = st.camera_input(
        "Take a picture"
    )

    if picture is None:
        return

    image = Image.open(
        picture
    ).convert("RGB")

    st.image(
        image,
        caption="Captured Image",
        use_container_width=True,
    )

    st.warning(
        "Camera detection is not connected "
        "to the Flask backend yet."
    )
