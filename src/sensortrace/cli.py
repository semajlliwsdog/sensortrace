from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from sensortrace.checks import inspect_records
from sensortrace.reporting import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sensortrace",
        description="Run explainable quality checks on environmental sensor CSV data.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="inspect a CSV file and write reports")
    check.add_argument("input", type=Path, help="path to input CSV")
    check.add_argument("--output-dir", type=Path, default=Path("sensortrace-report"))
    check.add_argument("--expected-interval-minutes", type=float, default=None)
    check.add_argument("--ranges-config", type=Path, default=None,
                       help="JSON file mapping property names to min/max limits")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.input.is_file():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 2
    try:
        with args.input.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                print("Error: CSV header row is missing.", file=sys.stderr)
                return 2
            records = list(reader)
        ranges = {}
        if args.ranges_config:
            ranges = json.loads(args.ranges_config.read_text(encoding="utf-8"))
            if not isinstance(ranges, dict):
                raise ValueError("Range configuration must be a JSON object.")
        report = inspect_records(records, args.expected_interval_minutes, ranges)
        json_path, html_path = write_reports(report, args.output_dir)
    except (OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    summary = report["summary"]
    print(f"Inspected {report['rows_inspected']} data row(s).")
    print(f"Errors: {summary['error']} | Warnings: {summary['warning']} | Info: {summary['info']}")
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    return 1 if summary["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
