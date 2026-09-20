"""
utils/depth_estimator.py

Runs Depth Anything V2 Metric Outdoor and estimates
a pothole's relative depth residual against a locally
fitted road surface.

IMPORTANT:
The residual is an estimated geometric signal from
monocular depth estimation. It is NOT a calibrated
physical pothole depth measurement in millimetres.
"""

from pathlib import Path

import numpy as np
from PIL import Image
import torch

from transformers import (
    AutoImageProcessor,
    AutoModelForDepthEstimation,
)

from utils.severity_estimator import estimate_severity


MODEL_NAME = (
    "depth-anything/"
    "Depth-Anything-V2-Metric-Outdoor-Small-hf"
)

ROAD_MARGIN = 50
INNER_RATIO = 0.20
MAX_ROAD_SAMPLES = 5000


_processor = None
_model = None


def get_depth_model():
    """Load the depth model once and reuse it."""

    global _processor
    global _model

    if _processor is None or _model is None:
        _processor = AutoImageProcessor.from_pretrained(
            MODEL_NAME
        )

        _model = AutoModelForDepthEstimation.from_pretrained(
            MODEL_NAME
        )

        _model.eval()

    return _processor, _model


def get_inner_box(
    x1,
    y1,
    x2,
    y2,
):
    """Shrink the YOLO bounding box."""

    width = x2 - x1
    height = y2 - y1

    return (
        x1 + width * INNER_RATIO,
        y1 + height * INNER_RATIO,
        x2 - width * INNER_RATIO,
        y2 - height * INNER_RATIO,
    )


def get_region_coordinates(
    depth_map,
    x1,
    y1,
    x2,
    y2,
):
    """Return valid coordinates and depth values."""

    height, width = depth_map.shape

    x1 = max(0, min(int(x1), width))
    y1 = max(0, min(int(y1), height))
    x2 = max(0, min(int(x2), width))
    y2 = max(0, min(int(y2), height))

    if x2 <= x1 or y2 <= y1:
        return (
            np.array([]),
            np.array([]),
            np.array([]),
        )

    region = depth_map[
        y1:y2,
        x1:x2
    ]

    yy, xx = np.mgrid[
        y1:y2,
        x1:x2
    ]

    values = region.reshape(-1)
    xx = xx.reshape(-1)
    yy = yy.reshape(-1)

    valid = np.isfinite(values)

    return (
        xx[valid].astype(float),
        yy[valid].astype(float),
        values[valid].astype(float),
    )


def get_surrounding_road_samples(
    depth_map,
    x1,
    y1,
    x2,
    y2,
):
    """Collect depth samples around the pothole."""

    height, width = depth_map.shape

    x1 = max(0, min(int(x1), width))
    y1 = max(0, min(int(y1), height))
    x2 = max(0, min(int(x2), width))
    y2 = max(0, min(int(y2), height))

    outer_x1 = max(
        0,
        x1 - ROAD_MARGIN
    )

    outer_y1 = max(
        0,
        y1 - ROAD_MARGIN
    )

    outer_x2 = min(
        width,
        x2 + ROAD_MARGIN
    )

    outer_y2 = min(
        height,
        y2 + ROAD_MARGIN
    )

    region = depth_map[
        outer_y1:outer_y2,
        outer_x1:outer_x2
    ]

    if region.size == 0:
        return (
            np.array([]),
            np.array([]),
            np.array([]),
        )

    yy, xx = np.mgrid[
        outer_y1:outer_y2,
        outer_x1:outer_x2
    ]

    # Remove the pothole bounding-box area.
    road_mask = ~(
        (xx >= x1)
        & (xx < x2)
        & (yy >= y1)
        & (yy < y2)
    )

    values = region[road_mask]
    xx_values = xx[road_mask]
    yy_values = yy[road_mask]

    valid = np.isfinite(values)

    xx_values = xx_values[
        valid
    ].astype(float)

    yy_values = yy_values[
        valid
    ].astype(float)

    values = values[
        valid
    ].astype(float)

    if values.size > MAX_ROAD_SAMPLES:

        rng = np.random.default_rng(42)

        indexes = rng.choice(
            values.size,
            size=MAX_ROAD_SAMPLES,
            replace=False,
        )

        xx_values = xx_values[indexes]
        yy_values = yy_values[indexes]
        values = values[indexes]

    return (
        xx_values,
        yy_values,
        values,
    )


def fit_road_plane(
    x,
    y,
    depth,
    image_width,
    image_height,
):
    """
    Fit:

        depth = a*x + b*y + c
    """

    if depth.size < 20:
        return None

    xn = x / max(
        image_width - 1,
        1
    )

    yn = y / max(
        image_height - 1,
        1
    )

    low = np.percentile(
        depth,
        5
    )

    high = np.percentile(
        depth,
        95
    )

    keep = (
        (depth >= low)
        & (depth <= high)
    )

    xn = xn[keep]
    yn = yn[keep]
    depth = depth[keep]

    if depth.size < 20:
        return None

    A = np.column_stack(
        [
            xn,
            yn,
            np.ones_like(xn),
        ]
    )

    coefficients, _, _, _ = np.linalg.lstsq(
        A,
        depth,
        rcond=None,
    )

    # Robust refinement.
    for _ in range(3):

        predicted = A @ coefficients

        residuals = (
            depth - predicted
        )

        median_residual = np.median(
            residuals
        )

        mad = np.median(
            np.abs(
                residuals
                - median_residual
            )
        )

        threshold = max(
            0.03,
            3.0 * 1.4826 * mad,
        )

        keep = (
            np.abs(
                residuals
                - median_residual
            )
            <= threshold
        )

        if np.sum(keep) < 20:
            break

        A = A[keep]
        depth = depth[keep]

        coefficients, _, _, _ = np.linalg.lstsq(
            A,
            depth,
            rcond=None,
        )

    return coefficients


def predict_plane(
    coefficients,
    x,
    y,
    image_width,
    image_height,
):
    """Predict expected road depth."""

    xn = x / max(
        image_width - 1,
        1
    )

    yn = y / max(
        image_height - 1,
        1
    )

    A = np.column_stack(
        [
            xn,
            yn,
            np.ones_like(xn),
        ]
    )

    return A @ coefficients


def estimate_pothole(
    depth_map,
    detection,
):
    """
    Estimate automatic severity signals for one pothole.

    Returns:
        dict or None
    """

    image_height, image_width = (
        depth_map.shape
    )

    x1 = detection["x_min"]
    y1 = detection["y_min"]
    x2 = detection["x_max"]
    y2 = detection["y_max"]

    # ---------------------------------------------------------
    # Surrounding road
    # ---------------------------------------------------------

    road_x, road_y, road_depth = (
        get_surrounding_road_samples(
            depth_map,
            x1,
            y1,
            x2,
            y2,
        )
    )

    coefficients = fit_road_plane(
        road_x,
        road_y,
        road_depth,
        image_width,
        image_height,
    )

    if coefficients is None:
        return {
            "severity": "undetermined",
            "residual_90": None,
            "positive_fraction": None,
        }

    # ---------------------------------------------------------
    # Inner pothole region
    # ---------------------------------------------------------

    ix1, iy1, ix2, iy2 = (
        get_inner_box(
            x1,
            y1,
            x2,
            y2,
        )
    )

    pothole_x, pothole_y, pothole_depth = (
        get_region_coordinates(
            depth_map,
            ix1,
            iy1,
            ix2,
            iy2,
        )
    )

    if pothole_depth.size == 0:
        return {
            "severity": "undetermined",
            "residual_90": None,
            "positive_fraction": None,
        }

    expected_depth = predict_plane(
        coefficients,
        pothole_x,
        pothole_y,
        image_width,
        image_height,
    )

    residuals = (
        pothole_depth
        - expected_depth
    )

    residual_90 = float(
        np.percentile(
            residuals,
            90
        )
    )

    positive_fraction = float(
        np.mean(
            residuals > 0.02
        )
    )

    severity = estimate_severity(
        residual_90,
        positive_fraction,
    )

    return {
        "severity": severity,
        "residual_90": residual_90,
        "positive_fraction": positive_fraction,
    }


def generate_depth_map(image):
    """Generate a depth map for a PIL image."""

    processor, model = get_depth_model()

    inputs = processor(
        images=image,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(**inputs)

    predicted_depth = (
        outputs.predicted_depth
    )

    prediction = (
        torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=image.size[::-1],
            mode="bicubic",
            align_corners=False,
        )
        .squeeze()
    )

    return prediction.cpu().numpy()


def analyze_image(
    image_path,
    detections,
):
    """
    Run depth estimation and calculate automatic
    severity for all YOLO detections.
    """

    image_path = Path(
        image_path
    )

    image = Image.open(
        image_path
    ).convert("RGB")

    depth_map = generate_depth_map(
        image
    )

    results = []

    for detection in detections:

        result = estimate_pothole(
            depth_map,
            detection,
        )

        results.append(result)

    return results