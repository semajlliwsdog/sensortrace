import json
from sensortrace.reporting import write_reports


def test_reports_are_written(tmp_path):
    report = {"rows_inspected": 0, "summary": {"error": 0, "warning": 0, "info": 0}, "findings": []}
    json_path, html_path = write_reports(report, tmp_path)
    assert json.loads(json_path.read_text())["rows_inspected"] == 0
    assert "SensorTrace data quality report" in html_path.read_text()
