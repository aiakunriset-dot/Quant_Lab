# Quant_Lab Dukascopy Acquisition Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fail-closed, resumable Dukascopy M1 acquisition engine for Quant_Lab covering 2019-01-02 through 2026-09-01 for the nine approved instruments while preserving immutable raw provenance.

**Architecture:** A planner creates deterministic hourly tick requests. A transport layer downloads raw `.bi5` artifacts with TLS verification, bounded retries and adaptive concurrency. Artifacts are hashed and recorded before decoding; a decoder converts 20-byte big-endian LZMA tick records to UTC ticks; a canonicalizer aggregates to M1 and validation gates reject corruption, duplicates, invalid OHLC, unexplained gaps, and scale anomalies.

**Tech Stack:** Python 3.14, httpx, Polars, PyArrow, Pydantic, SQLite metadata, pytest, Hypothesis, Ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-09-17-dukascopy-acquisition-design.md`

## Global Constraints

- Project root: `C:\QUANT_LAB` and project name: `Quant_Lab`.
- Historical interval: `[2019-01-02T00:00:00Z, 2026-09-01T00:00:00Z)`.
- Primary acquisition grain: M1 derived from Dukascopy tick data; no synthetic candles.
- Preserve immutable raw `.bi5` artifacts and SHA-256 provenance.
- TLS certificate verification remains enabled; no insecure bypass.
- Missing weekend/holiday data is classified explicitly as `NO_DATA`, not silently repaired.
- Partial/corrupt data fails closed.
- Approved instruments: usa30idxusd, usa500idxusd, usatechidxusd, deuidxeur, gbridxgbp, jpnidxjpy, xauusd, dollaridxusd, volidxusd.

---

### Task 1: Acquisition contracts and planner

**Files:**
- Create: `src/quantlab/acquisition/contracts.py`
- Create: `src/quantlab/acquisition/planner.py`
- Test: `tests/unit/acquisition/test_planner.py`

- [ ] Write failing tests for interval semantics, zero-based month mapping, approved instrument validation, and deterministic chunk planning.
- [ ] Run `pytest tests/unit/acquisition/test_planner.py -v` and verify RED.
- [ ] Implement typed immutable contracts and deterministic hourly request planning.
- [ ] Run the focused tests and verify GREEN.

### Task 2: Retry and HTTP transport

**Files:**
- Create: `src/quantlab/acquisition/retry.py`
- Create: `src/quantlab/acquisition/transport.py`
- Test: `tests/unit/acquisition/test_transport.py`

- [ ] Write failing tests for retryable HTTP statuses, timeout retry, 404/no-data classification, bounded attempts, and deterministic backoff calculation.
- [ ] Verify RED.
- [ ] Implement TLS-verified HTTP transport and retry policy.
- [ ] Verify GREEN.

### Task 3: Raw artifacts and manifest

**Files:**
- Create: `src/quantlab/acquisition/artifacts.py`
- Create: `src/quantlab/acquisition/metadata.py`
- Test: `tests/unit/acquisition/test_artifacts.py`

- [ ] Write failing tests for atomic raw writes, SHA-256, duplicate prevention, and manifest state transitions.
- [ ] Verify RED.
- [ ] Implement immutable artifact storage and SQLite manifest.
- [ ] Verify GREEN.

### Task 4: Dukascopy decoder

**Files:**
- Create: `src/quantlab/acquisition/decoder.py`
- Test: `tests/unit/acquisition/test_decoder.py`
- Test: `tests/property/acquisition/test_decoder_properties.py`

- [ ] Write failing tests for valid 20-byte records, malformed payload rejection, timestamp reconstruction, and scale conversion.
- [ ] Verify RED.
- [ ] Implement raw-LZMA decoder using explicit big-endian record parsing.
- [ ] Verify unit and property tests.

### Task 5: Canonical M1 aggregation and validation

**Files:**
- Create: `src/quantlab/acquisition/canonical.py`
- Create: `src/quantlab/acquisition/validation.py`
- Test: `tests/unit/acquisition/test_canonical.py`
- Test: `tests/unit/acquisition/test_validation.py`

- [ ] Write failing tests for OHLC invariants, timestamp monotonicity, duplicate rejection, spread/volume handling, and deterministic aggregation.
- [ ] Verify RED.
- [ ] Implement canonical M1 conversion and fail-closed validation.
- [ ] Verify GREEN.

### Task 6: Service orchestration and CLI

**Files:**
- Create: `src/quantlab/acquisition/service.py`
- Create: `src/quantlab/acquisition/dukascopy.py`
- Modify: `src/quantlab/cli/main.py`
- Modify: `pyproject.toml`
- Test: `tests/unit/acquisition/test_service.py`

- [ ] Write failing service tests for resume, dry-run planning, fail-fast fatal errors, and successful commit ordering.
- [ ] Verify RED.
- [ ] Implement orchestration and CLI commands `quantlab acquisition plan`, `quantlab acquisition download`, and `quantlab acquisition status`.
- [ ] Verify GREEN.

### Task 7: Verification and bulk acquisition launcher

**Files:**
- Create: `tools/run_dukascopy.ps1`
- Create: `docs/DATA_ACQUISITION.md`
- Test: full test suite

- [ ] Run Ruff, mypy, pytest, and CLI smoke tests.
- [ ] Run a network smoke test against one known hour before bulk acquisition.
- [ ] Execute bulk acquisition only after smoke verification succeeds.
- [ ] Verify manifests, artifact hashes, canonical M1 counts, and failure ledger.
