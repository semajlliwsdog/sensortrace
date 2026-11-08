from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

REQUIRED_COLUMNS = ("timestamp", "sensor_id", "property", "value", "unit")


def _finding(severity: str, code: str, message: str, rows: list[int] | None = None,
             details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message,
            "rows": rows or [], "details": details or {}}


def inspect_records(records: list[dict[str, str]], expected_interval_minutes: float | None = None,
                    ranges: dict[str, dict[str, float]] | None = None) -> dict[str, Any]:
    """Inspect CSV records. Row numbers are 1-based data rows (header is row 1)."""
    findings: list[dict[str, Any]] = []
    if not records:
        return {"rows_inspected": 0, "summary": {"error": 1, "warning": 0, "info": 0},
                "findings": [_finding("error", "EMPTY_DATASET", "The CSV contains no data rows.")]}

    groups: dict[tuple[str, str], list[tuple[datetime, int, float]]] = defaultdict(list)
    duplicate_keys: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    numeric_values: dict[str, list[tuple[float, int]]] = defaultdict(list)
    previous: dict[tuple[str, str], tuple[datetime, int]] = {}

    for index, record in enumerate(records, start=2):
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in record]
        if missing_columns:
            findings.append(_finding("error", "MISSING_COLUMNS",
                f"Required column(s) absent: {', '.join(missing_columns)}.", [index]))
            continue
        empty = [col for col in REQUIRED_COLUMNS if not str(record.get(col, "")).strip()]
        if empty:
            findings.append(_finding("error", "MISSING_VALUE",
                f"Required value(s) missing: {', '.join(empty)}.", [index]))
            continue
        try:
            timestamp = datetime.fromisoformat(record["timestamp"].strip().replace("Z", "+00:00"))
        except ValueError:
            findings.append(_finding("error", "INVALID_TIMESTAMP",
                "Timestamp is not parseable as ISO 8601.", [index], {"value": record["timestamp"]}))
            continue
        try:
            value = float(record["value"])
        except (TypeError, ValueError):
            findings.append(_finding("error", "NON_NUMERIC_VALUE",
                "Measurement value must be numeric.", [index], {"value": record["value"]}))
            continue
        if value != value or value in (float("inf"), float("-inf")):
            findings.append(_finding("error", "NON_FINITE_VALUE",
                "Measurement value must be finite.", [index]))
            continue

        sensor, prop, unit = record["sensor_id"].strip(), record["property"].strip(), record["unit"].strip()
        key = (sensor, prop)
        duplicate_keys[(sensor, prop, record["timestamp"].strip())].append(index)
        groups[key].append((timestamp, index, value))
        numeric_values[prop].append((value, index))

        if key in previous and timestamp < previous[key][0]:
            findings.append(_finding("warning", "OUT_OF_ORDER",
                "Timestamp is earlier than the preceding row for this sensor/property series.",
                [previous[key][1], index]))
        previous[key] = (timestamp, index)

        if ranges and prop in ranges:
            limits = ranges[prop]
            lower, upper = limits.get("min"), limits.get("max")
            if lower is not None and value < lower:
                findings.append(_finding("warning", "BELOW_CONFIGURED_RANGE",
                    f"Value is below the configured minimum for {prop}.", [index],
                    {"value": value, "minimum": lower, "unit": unit}))
            if upper is not None and value > upper:
                findings.append(_finding("warning", "ABOVE_CONFIGURED_RANGE",
                    f"Value is above the configured maximum for {prop}.", [index],
                    {"value": value, "maximum": upper, "unit": unit}))

    for (sensor, prop, timestamp), row_numbers in duplicate_keys.items():
        if len(row_numbers) > 1:
            findings.append(_finding("warning", "DUPLICATE_OBSERVATION",
                f"Repeated timestamp for sensor '{sensor}' and property '{prop}'.",
                row_numbers, {"timestamp": timestamp}))

    if expected_interval_minutes is not None:
        if expected_interval_minutes <= 0:
            findings.append(_finding("error", "INVALID_EXPECTED_INTERVAL",
                "Expected interval must be greater than zero."))
        else:
            threshold_seconds = expected_interval_minutes * 60 * 1.5
            for (sensor, prop), observations in groups.items():
                ordered = sorted(observations, key=lambda item: item[0])
                for left, right in zip(ordered, ordered[1:]):
                    seconds = (right[0] - left[0]).total_seconds()
                    if seconds > threshold_seconds:
                        findings.append(_finding("warning", "SAMPLING_GAP",
                            f"Gap exceeds 1.5 times the expected interval for '{sensor}' / '{prop}'.",
                            [left[1], right[1]],
                            {"gap_minutes": round(seconds / 60, 3),
                             "expected_interval_minutes": expected_interval_minutes}))

    for prop, items in numeric_values.items():
        values = sorted(value for value, _ in items)
        if len(values) < 4:
            continue
        q1, q3 = _percentile(values, 25), _percentile(values, 75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        for value, row in items:
            if value < lower or value > upper:
                findings.append(_finding("info", "POTENTIAL_IQR_OUTLIER",
                    f"Value is outside the 1.5 × IQR fences for '{prop}'; review in context.",
                    [row], {"value": value, "lower_fence": lower, "upper_fence": upper}))

    summary = {level: sum(1 for item in findings if item["severity"] == level)
               for level in ("error", "warning", "info")}
    return {"rows_inspected": len(records), "summary": summary, "findings": findings}


def _percentile(values: list[float], percentile: float) -> float:
    """Linearly interpolated percentile (inclusive method)."""
    if len(values) == 1:
        return values[0]
    position = (len(values) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower
    return values[lower] + (values[upper] - values[lower]) * fraction
