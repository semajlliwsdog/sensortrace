from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def write_reports(report: dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    json_path, html_path = destination / "report.json", destination / "report.html"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    rows = []
    for finding in report["findings"]:
        rows.append("<tr>" +
            f"<td>{html.escape(finding['severity'].upper())}</td>" +
            f"<td>{html.escape(finding['code'])}</td>" +
            f"<td>{html.escape(finding['message'])}</td>" +
            f"<td>{html.escape(', '.join(map(str, finding['rows'])) or '—')}</td></tr>")
    summary = report["summary"]
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SensorTrace data quality report</title>
<style>
body{{font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#202938}}
h1{{margin-bottom:.2rem}} .muted{{color:#596579}} .stats{{display:flex;gap:1rem;flex-wrap:wrap}}
.stats div{{padding:1rem;border:1px solid #d7dde5;border-radius:8px;min-width:100px}}
table{{border-collapse:collapse;width:100%;margin-top:1.5rem}} th,td{{text-align:left;padding:.7rem;border-bottom:1px solid #d7dde5;vertical-align:top}}
th{{background:#f2f5f8}}
</style></head><body>
<h1>SensorTrace data quality report</h1>
<p class="muted">Rows inspected: {report['rows_inspected']}</p>
<div class="stats">
<div><strong>{summary['error']}</strong><br>Errors</div>
<div><strong>{summary['warning']}</strong><br>Warnings</div>
<div><strong>{summary['info']}</strong><br>Informational flags</div>
</div>
<table><thead><tr><th>Severity</th><th>Check</th><th>Finding</th><th>CSV row(s)</th></tr></thead>
<tbody>{''.join(rows) if rows else '<tr><td colspan="4">No findings.</td></tr>'}</tbody></table>
<p class="muted">Findings require interpretation. They do not prove sensor malfunction or measurement inaccuracy.</p>
</body></html>"""
    html_path.write_text(document, encoding="utf-8")
    return json_path, html_path
