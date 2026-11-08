# Methodology and interpretation

SensorTrace is a first-pass data-quality screening utility. It reports observable characteristics of the supplied file; it does not certify the truth of a measurement.

| Check | Rule | Severity |
|---|---|---|
| Required values | Required field absent or blank | Error |
| Timestamp | Timestamp cannot be parsed as ISO 8601 | Error |
| Numeric value | Value cannot be parsed as a finite number | Error |
| Duplicate observation | Same sensor, property and timestamp appears more than once | Warning |
| Row order | Timestamp is earlier than the preceding row for that sensor/property | Warning |
| Sampling gap | Adjacent sorted observations are more than 1.5 × configured interval apart | Warning |
| Configured range | Value is below/above user-supplied property limits | Warning |
| IQR outlier | Value lies outside Q1 − 1.5×IQR or Q3 + 1.5×IQR | Info |

## Why flags are not diagnoses

A value outside a configured range may be a real event, a unit mismatch, a configuration error or a sensor issue. An IQR outlier is distribution-dependent; genuine extremes can be important observations. SensorTrace therefore flags rather than deletes, clips, imputes or corrects values.

The IQR rule is skipped when fewer than four valid values exist for a property or when the interquartile range is zero. Quartiles use linear interpolation.

## Sampling-gap rule

When `--expected-interval-minutes` is supplied, observations are sorted by timestamp within each `(sensor_id, property)` group. A gap is flagged when it exceeds 1.5 times the expected interval. This is a configurable screening heuristic, not a universal definition of missing data.

## Research basis

The W3C/OGC Semantic Sensor Network model distinguishes sensors, observations, observed properties and phenomenon times. SensorTrace uses a compact CSV representation rather than implementing the full ontology.

Research on meteorological time-series QA/QC identifies duplicate timestamps, gaps, extremes and time ordering as practical challenges. A systematic review of sensor data quality also discusses missing data, outliers, bias and drift. This initial release implements only transparent file-level checks; it does not attempt advanced drift diagnosis or imputation.
