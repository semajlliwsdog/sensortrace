# Data format

SensorTrace accepts UTF-8 CSV files with a header row and these required fields:

- `timestamp`: ISO 8601 date-time string. Include `Z` or an explicit UTC offset where possible.
- `sensor_id`: stable identifier for the sensor or data source.
- `property`: observed property name, e.g. `temperature_c`.
- `value`: finite numeric value.
- `unit`: unit string, e.g. `°C` or `%`.

`location` and other additional columns may be present. The current release does not interpret them.

## Observation identity

For duplicate detection, SensorTrace treats `(sensor_id, property, timestamp)` as the observation key. Two records with that key are flagged even if their values match.

## Time handling

ISO 8601 timestamps are parsed into Python datetime objects. Keep timestamps consistently timezone-aware or consistently naive within a dataset. The tool does not infer missing time zones or convert local wall-clock times into UTC.

## Example

```csv
timestamp,sensor_id,property,value,unit
2026-10-01T08:00:00Z,SENSOR-A,temperature_c,22.1,°C
2026-10-01T08:15:00Z,SENSOR-A,temperature_c,22.4,°C
```
