from sensortrace.checks import inspect_records


def row(timestamp="2026-10-01T08:00:00Z", value="22.0", sensor="A", prop="temperature_c"):
    return {"timestamp": timestamp, "sensor_id": sensor, "property": prop,
            "value": value, "unit": "°C"}


def codes(report):
    return {finding["code"] for finding in report["findings"]}


def test_empty_dataset_is_error():
    report = inspect_records([])
    assert "EMPTY_DATASET" in codes(report)
    assert report["summary"]["error"] == 1


def test_duplicate_observation_is_flagged():
    report = inspect_records([row(), row(value="23.0")])
    assert "DUPLICATE_OBSERVATION" in codes(report)


def test_invalid_timestamp_and_numeric_value_are_flagged():
    report = inspect_records([row(timestamp="not-a-date"), row(timestamp="2026-10-01T08:15:00Z", value="bad")])
    assert {"INVALID_TIMESTAMP", "NON_NUMERIC_VALUE"} <= codes(report)


def test_out_of_order_is_flagged():
    report = inspect_records([
        row("2026-10-01T08:15:00Z"),
        row("2026-10-01T08:00:00Z", value="21.0"),
    ])
    assert "OUT_OF_ORDER" in codes(report)


def test_configured_range_is_flagged():
    report = inspect_records([row(value="42")], ranges={"temperature_c": {"max": 35}})
    assert "ABOVE_CONFIGURED_RANGE" in codes(report)


def test_sampling_gap_is_flagged():
    report = inspect_records([
        row("2026-10-01T08:00:00Z"),
        row("2026-10-01T09:00:00Z", value="23"),
    ], expected_interval_minutes=15)
    assert "SAMPLING_GAP" in codes(report)


def test_iqr_outlier_is_informational():
    values = ["20", "21", "20", "22", "100"]
    records = [row(f"2026-10-01T08:{i*5:02d}:00Z", value=v) for i, v in enumerate(values)]
    report = inspect_records(records)
    assert "POTENTIAL_IQR_OUTLIER" in codes(report)
    assert report["summary"]["info"] >= 1
