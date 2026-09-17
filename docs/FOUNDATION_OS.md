# Quant_Lab Foundation OS

## Control Plane

`C:\QUANT_LAB` is the permanent local control-plane root.

| System | Role | Source of truth |
|---|---|---|
| GPT | architecture/research/debugging agent | no |
| Claude | independent/adversarial review agent | no |
| Aider | local implementation agent | no |
| Git/GitHub | source control | **yes for code** |
| Google Drive | datasets/artifacts/reports | **yes for artifacts** |
| Colab | remote compute/backtest/ML | no |

## Required invariants

- All code changes are Git-visible.
- Aider auto-commit is disabled in the project policy so orchestration can own promotion gates.
- TLS verification is mandatory.
- Credentials are represented only by environment-variable names in configuration.
- Task state is persisted in the local control ledger.
- Artifact identity is SHA-256 based.
- Colab execution is reproducible from Git revision + dataset IDs + configuration hash + seed.

## Drive namespace

```text
Quant_Lab/
  datasets/
  experiments/
  backtests/
  models/
  reports/
  runs/
```

Colab should read a run manifest and write results into the corresponding immutable run namespace. Canonical Python source remains in GitHub.

## Agent workflow

```text
request
  -> task contract
  -> ledger
  -> agent execution
  -> Git/artifact changes
  -> verification
  -> promotion
```

GPT and Claude can propose or review. Aider can modify local code. Promotion requires verification and Git evidence.
