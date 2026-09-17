# Architecture

RAW ACQUISITION
-> CANONICAL RAW
-> VALIDATION
-> DETERMINISTIC TRANSFORMATION
-> DATASET RELEASE
-> FEATURES/TARGETS
-> RESEARCH
-> BACKTEST
-> STATISTICAL GATES
-> STRATEGY PROMOTION
-> PRODUCTION

Non-negotiable:
- UTC canonical timestamps.
- No synthetic market bars.
- No forward/back fill to hide gaps.
- Duplicate timestamps require reconciliation or quarantine.
- Invalid records are not silently discarded.
- Published datasets require identity, provenance and checksum.
