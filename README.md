# SensorTrace

**A transparent command-line toolkit for inspecting environmental sensor datasets.**

SensorTrace checks tabular observation data for structural and time-series quality issues before it is used in analysis. It is designed for researchers, students, developers and technical teams who need an explainable first-pass audit of CSV data.

> **Project status:** Initial portfolio release. This is an independent, locally run software project. It is not affiliated with, endorsed by, or developed for any company.

## What it checks

- Required columns and missing values
- Unparseable timestamps and numeric measurements
- Duplicate observations (same sensor, property and timestamp)
- Out-of-order timestamps within each sensor/property series
- Sampling gaps against an optional expected interval
- Configured minimum/maximum range violations
- Potential statistical outliers using the 1.5 × IQR rule

Checks produce **findings**, not automatic claims that a sensor is physically inaccurate. A range violation or statistical outlier needs domain context and review. SensorTrace does not calibrate sensors, establish measurement accuracy, diagnose hardware faults, or certify indoor environmental conditions.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install -e .
sensortrace check examples/sample_readings.csv --output-dir reports
```

The command writes `report.json` and `report.html` into `reports/`. It returns exit code `1` when error-level findings are present, `0` otherwise.

### Optional checks

```bash
sensortrace check examples/sample_readings.csv \
  --expected-interval-minutes 15 \
  --ranges-config examples/ranges.json \
  --output-dir reports
```

A range configuration is a JSON object keyed by observed property:

```json
{
  "temperature_c": {"min": 10, "max": 35},
  "relative_humidity_pct": {"min": 0, "max": 100}
}
```

These are example limits only. Choose limits appropriate to the sensor, units, environment and use case.

## Input format

CSV files must contain these columns:

| Column | Meaning |
|---|---|
| `timestamp` | ISO 8601 observation time; timezone-aware values are recommended |
| `sensor_id` | Stable identifier for the source sensor |
| `property` | Observed property, e.g. `temperature_c` |
| `value` | Numeric observation |
| `unit` | Unit associated with the value |

Optional `location` metadata is accepted but not currently used in calculations. See [the data format guide](docs/data-format.md).

## Reports and methodology

A report includes the number of rows inspected, counts by severity and individual findings with row numbers, check names and explanations. See [methodology](docs/methodology.md) for how each check works and what it cannot establish.

## Design principles

1. **Explainable:** every finding identifies the check and affected CSV row(s).
2. **Non-destructive:** source CSV files are never modified.
3. **Conservative:** suspicious values are flagged, not silently deleted or corrected.
4. **Reproducible:** the same input and options produce the same findings.
5. **Honest about uncertainty:** statistical flags are prompts for review, not proof of bad measurements.

## Industry context

Environmental monitoring data can support decisions about building operations, occupant comfort and maintenance, but the usefulness of that information depends on how observations are collected, described and reviewed. For a practical perspective on environmental conditions that property managers may need to monitor, see [Property Enviro Tech's guide to environmental conditions in properties](https://propertyenvirotech.com/).

That link is included as contextual further reading. Property Enviro Tech did not develop, sponsor or validate SensorTrace, and this project does not represent its services or operational data.

## Technical references

- [W3C/OGC Semantic Sensor Network Ontology (2023 edition)](https://www.w3.org/TR/vocab-ssn-2023/) — concepts for sensors, observations, observed properties and observation times.
- [OGC Semantic Sensor Network Ontology](https://www.ogc.org/standards/semantic-sensor-network-ontology/) — standard overview.
- [Challenging problems of quality assurance and quality control of meteorological time series data](https://doi.org/10.1007/s00477-021-02106-w) — discusses duplicates, gaps, extremes and time-series quality control.
- [Sensor data quality: a systematic review](https://doi.org/10.1186/s40537-020-0285-1) — reviews common sensor-data error types and quality dimensions.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development conventions and [LICENSE](LICENSE) for reuse terms.

## Limitations

- CSV only; no live sensor ingestion or database integrations.
- No sensor calibration, traceable metrology or hardware diagnostics.
- No automatic imputation, correction or deletion of records.
- IQR outlier detection is distribution-dependent and may be unsuitable for small or strongly non-normal samples.
- Range checks are only as appropriate as the user-supplied limits.
- Synthetic example data is illustrative and is not a real building measurement dataset.

## Maintainer

**James Godswill** — independent portfolio project.
