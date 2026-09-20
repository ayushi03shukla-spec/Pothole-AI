"""
utils/severity_estimator.py

Automatic pothole severity estimation based on the
depth residual produced by the depth-estimation pipeline.

IMPORTANT:
These thresholds are project heuristics based on the
tested depth-model residuals. They are not calibrated
physical pothole-depth thresholds in millimetres.
"""


HIGH_RESIDUAL_THRESHOLD = 0.15
HIGH_AREA_THRESHOLD = 0.50

MEDIUM_RESIDUAL_THRESHOLD = 0.06
MEDIUM_AREA_THRESHOLD = 0.25


def estimate_severity(
    residual_90,
    positive_fraction,
):
    """
    Estimate pothole severity from depth-model signals.

    Parameters:
        residual_90 (float):
            90th-percentile residual in metres.

        positive_fraction (float):
            Fraction of the pothole region with a
            positive depth residual, represented
            as a value between 0 and 1.

    Returns:
        str:
            'high'
            'medium'
            'low'
            'undetermined'
    """

    if residual_90 is None:
        return "undetermined"

    if positive_fraction is None:
        return "undetermined"

    try:
        residual_90 = float(residual_90)
        positive_fraction = float(positive_fraction)
    except (TypeError, ValueError):
        return "undetermined"

    if residual_90 < 0:
        residual_90 = 0.0

    positive_fraction = max(
        0.0,
        min(positive_fraction, 1.0)
    )

    # High severity
    if (
        residual_90 >= HIGH_RESIDUAL_THRESHOLD
        and positive_fraction >= HIGH_AREA_THRESHOLD
    ):
        return "high"

    # Medium severity
    if (
        residual_90 >= MEDIUM_RESIDUAL_THRESHOLD
        and positive_fraction >= MEDIUM_AREA_THRESHOLD
    ):
        return "medium"

    # Otherwise low
    return "low"