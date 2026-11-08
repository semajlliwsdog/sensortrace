# Contributing

Thanks for considering a contribution.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Guidelines

- Keep checks deterministic and explainable.
- Add or update tests for behaviour changes.
- Never silently modify source observations.
- Document assumptions, thresholds and limitations.
- Use synthetic data in examples unless dataset provenance and permission are clear.
- Avoid presenting flags as proof of sensor failure or measurement inaccuracy.

For substantial changes, open an issue describing the use case and proposed approach first.
