# Foundation OS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build the Quant_Lab local control plane contracts, configuration, task ledger, artifact provenance, environment doctor, Aider/Git guardrails and Colab/Drive handoff manifest without making external network calls during tests.

**Architecture:** A provider-neutral orchestration core persists immutable task attempts and artifact references. Local execution uses subprocesses for Git/Aider while cloud integrations are represented by validated contracts and handoff manifests until credentials are deliberately configured.

**Tech Stack:** Python 3.14, stdlib, Pydantic 2, SQLite, pytest, Hypothesis.

**Spec:** `docs/superpowers/specs/2026-09-17-foundation-os-design.md`

## Global Constraints
- Project root is permanently `C:\QUANT_LAB`.
- Canonical repository is `aiakunriset-dot/Quant_Lab`.
- Secrets are never stored in source, manifests, logs or task records.
- Google Drive is artifact/data storage; GitHub is canonical source control.
- Colab is remote compute and must consume explicit Git/artifact identities.
- Aider edits are verified through Git diff and tests before promotion.
- No external network call is made by unit tests.

---

### Task 1: Orchestration contracts
**Files:** Create `src/quantlab/orchestration/contracts.py`, Test `tests/unit/orchestration/test_contracts.py`.
- [ ] Write failing tests for provider/role enums, task identity, artifact identity and state-transition rules.
- [ ] Run the focused test and verify it fails because contracts are absent.
- [ ] Implement typed immutable contracts with validation and deterministic serialization.
- [ ] Run focused tests and verify PASS.

### Task 2: Configuration boundary
**Files:** Create `src/quantlab/orchestration/config.py`, Test `tests/unit/orchestration/test_config.py`.
- [ ] Test root-path enforcement, environment-variable presence detection, and secret redaction.
- [ ] Verify RED state.
- [ ] Implement configuration loading without persisting secret values.
- [ ] Verify GREEN state.

### Task 3: SQLite task ledger
**Files:** Create `src/quantlab/orchestration/ledger.py`, Test `tests/unit/orchestration/test_ledger.py`.
- [ ] Test create task, legal transitions, illegal backward transition, attempt history and idempotent lookup.
- [ ] Verify RED state.
- [ ] Implement transactional SQLite ledger with monotonic attempts.
- [ ] Verify GREEN state.

### Task 4: Artifact provenance
**Files:** Create `src/quantlab/orchestration/artifacts.py`, Test `tests/unit/orchestration/test_artifacts.py`.
- [ ] Test SHA-256 calculation, manifest serialization and mismatch detection.
- [ ] Verify RED state.
- [ ] Implement immutable artifact records and hashing.
- [ ] Verify GREEN state.

### Task 5: Git/Aider execution guard
**Files:** Create `src/quantlab/orchestration/local.py`, Test `tests/unit/orchestration/test_local.py`.
- [ ] Test command argument isolation, project-root enforcement, Git status capture and Aider command construction.
- [ ] Verify RED state.
- [ ] Implement subprocess runner and non-secret environment filtering.
- [ ] Verify GREEN state.

### Task 6: Colab/Drive handoff
**Files:** Create `src/quantlab/orchestration/handoff.py`, Test `tests/unit/orchestration/test_handoff.py`.
- [ ] Test deterministic run manifest hash, required Git revision, dataset artifact IDs and Drive path validation.
- [ ] Verify RED state.
- [ ] Implement handoff manifest generation; no direct network dependency.
- [ ] Verify GREEN state.

### Task 7: Environment doctor CLI
**Files:** Modify `src/quantlab/cli/main.py`; Create `src/quantlab/orchestration/doctor.py`; Test `tests/unit/orchestration/test_doctor.py`.
- [ ] Test classification of configured/missing tools without leaking secrets.
- [ ] Verify RED state.
- [ ] Implement local diagnostics for Python, Git, Aider, repository identity and provider configuration.
- [ ] Verify GREEN state.

### Task 8: Integration verification
**Files:** Modify `README.md`, `docs/DEVELOPMENT.md`, `.gitignore` only as required.
- [ ] Run focused orchestration tests.
- [ ] Run full pytest suite.
- [ ] Run compile, Ruff and mypy checks available in the environment.
- [ ] Run CLI doctor in dry/local mode.
- [ ] Review diff for secret leakage and forbidden naming.
- [ ] Package a reproducible foundation archive.
