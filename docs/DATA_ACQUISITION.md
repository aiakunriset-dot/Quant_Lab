# Quant_Lab Dukascopy Acquisition

## Coverage

The approved historical coverage is:

- Start: `2019-01-02T00:00:00Z`
- End: `2026-09-01T00:00:00Z`
- Interval: `[start, end)`
- Primary source grain: hourly Dukascopy `.bi5` ticks
- Canonical research grain: M1

Approved instruments:

`usa30idxusd`, `usa500idxusd`, `usatechidxusd`, `deuidxeur`, `gbridxgbp`, `jpnidxjpy`, `xauusd`, `dollaridxusd`, `volidxusd`.

## Execution on Windows

From `C:\QUANT_LAB` with the project virtual environment active:

```powershell
.\.venv\Scripts\python.exe -m quantlab.cli.main acquisition plan --instrument usa500idxusd --start 2019-01-02T00:00:00Z --end 2026-09-01T00:00:00Z --root data
```

Run the actual acquisition only after the plan output is reviewed:

```powershell
.\.venv\Scripts\python.exe -m quantlab.cli.main acquisition download --instrument usa500idxusd --start 2019-01-02T00:00:00Z --end 2026-09-01T00:00:00Z --root data --workers 2
```

The provided `tools\run_dukascopy.ps1` wraps the same command and keeps the project root fixed at `C:\QUANT_LAB`.

## Integrity rules

Raw `.bi5` files are written atomically and hashed with SHA-256. The manifest is SQLite-backed. A previously validated artifact is skipped only when the file still exists and its current SHA-256 equals the manifest value.

404 is classified as `NO_DATA`. Transport errors retry with bounded exponential backoff. TLS certificate verification is never disabled.

## Important scale rule

Dukascopy documents that non-FX instruments require instrument-specific price-scale verification. Quant_Lab therefore does not silently apply the generic FX divisor to indices, metals, or volatility instruments. Raw acquisition can proceed independently; canonical decoding must use a verified instrument specification.
