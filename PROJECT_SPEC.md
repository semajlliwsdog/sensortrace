# SensorTrace — project specification

## Purpose
A local CLI for transparent, explainable first-pass quality screening of environmental sensor CSV datasets.

## Users
Students, researchers, data analysts and developers working with structured sensor observations.

## Core workflow
CSV input → schema/value checks → time-series checks → JSON + HTML reports.

## Scope of v0.1
Required-field validation, timestamp and numeric parsing, duplicates, row ordering, optional sampling gaps, optional configured limits and IQR review flags.

## Explicit non-goals
Live device connectivity, calibration, hardware diagnostics, automated correction/imputation, regulatory certification, building-condition assessment.

## Data provenance
The bundled sample is synthetic and illustrative. It is not a record of measurements from a real building or sensor deployment.

## Backlink placement
The README contains one contextual further-reading link to Property Enviro Tech. The project remains independently owned and maintained by James Godswill.
