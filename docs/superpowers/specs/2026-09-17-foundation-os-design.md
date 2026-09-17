# Quant_Lab Foundation OS Design

## Goal
Build a deterministic local control plane for orchestrating GPT, Claude, Aider, Git/GitHub, Google Drive and Colab without allowing any agent or compute environment to become the source of truth for Quant_Lab code.

## Architecture
The Windows workstation at `C:\QUANT_LAB` is the control plane. Git/GitHub are the canonical code and version-control plane; Google Drive is the artifact/data plane; Colab is the remote compute plane; GPT, Claude and Aider are replaceable execution agents behind explicit task contracts. The first implementation is provider-neutral and fail-closed: credentials are referenced through environment variables, task state is persisted locally, and external execution is only enabled when explicitly configured.

## Source-of-truth rules
1. Project root is permanently `C:\QUANT_LAB`.
2. Canonical source code is Git-tracked and synchronized with `aiakunriset-dot/Quant_Lab`.
3. Google Drive stores large datasets, notebooks, model artifacts and reports, not canonical source code.
4. Colab consumes immutable Git revisions and declared Drive artifacts; it must emit a run manifest and result artifact identity.
5. GPT/Claude are advisory or execution agents but never authorities over repository state.
6. Aider is a local code executor and must operate inside Git with explicit auditability.
7. Secrets never enter Git, manifests, task payloads, logs or notebooks.
8. Every orchestration task has an immutable task ID, requested agent, repository revision, input artifact references and result state.

## Agent roles
- `gpt`: architecture, research synthesis, debugging and controlled tool execution.
- `claude`: independent review, adversarial reasoning and second-opinion analysis.
- `aider`: local implementation and test execution against the Git worktree.
- `colab`: isolated compute/backtest/ML execution.
- `github`: source-control transport and review surface.
- `gdrive`: artifact/data transport and archival.

## State machine
`PLANNED -> RUNNING -> SUCCEEDED | FAILED | CANCELLED`.
A task cannot transition backwards. Retry creates a new attempt under the same task ID rather than mutating historical attempts.

## Artifact contract
Every material output is represented by an artifact record containing logical name, URI/path, SHA-256, producer, task ID, Git revision when applicable, creation timestamp and schema version.

## Security boundary
The control plane only records whether a required environment variable is configured; it never logs or persists the secret value. Provider API calls must use TLS verification. No `verify=False`, plaintext credential files, or committed `.env` files are permitted.

## Colab handoff
A Colab run is represented by a manifest containing Git revision, dataset artifact IDs, configuration hash, Python/package lock identity, random seeds, start/end timestamps and result artifact IDs. The notebook is reproducible from the manifest rather than relying on mutable Drive state.

## Drive layout
`Quant_Lab/{datasets,experiments,backtests,models,reports,runs}`. Each run receives an immutable run directory keyed by task ID and timestamp.

## Git/Aider policy
Aider is configured for Git integration, but orchestration does not blindly accept Aider commits. The control plane records the pre-execution SHA and post-execution SHA, then verification must inspect the diff and run the required test suite before promotion.

## Failure policy
Missing credentials, dirty repository state when a clean state is required, unavailable Git remote, missing artifact, checksum mismatch, unsupported provider, or failed verification are explicit failures. The system must not silently downgrade to an alternative provider or silently create synthetic data.

## External references
- OpenAI Responses API supports tools/function calling for external actions.
- Anthropic Claude supports tool use with explicit tool definitions.
- Google Drive supports OAuth and resumable uploads; permissions are explicit ACL resources.
- Colab notebooks are stored in Google Drive and provide browser-based compute.
- Aider integrates directly with Git and supports repo-local `.aider.conf.yml` and `.env` configuration.
