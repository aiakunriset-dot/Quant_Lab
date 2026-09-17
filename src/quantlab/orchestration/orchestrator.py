from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quantlab.orchestration.contracts import AgentProvider, Task, TaskState
from quantlab.orchestration.ledger import TaskLedger


@dataclass(frozen=True, slots=True)
class ExecutionHandle:
    """Immutable handle used to correlate an execution with its task ledger entry."""

    task_id: str
    attempt: int
    provider: AgentProvider


class ControlPlane:
    """Deterministic orchestration facade over the local task ledger."""

    def __init__(self, database: Path) -> None:
        """Initialize the control plane using a local SQLite ledger."""
        self.ledger = TaskLedger(database)

    def plan(self, name: str, provider: AgentProvider) -> Task:
        """Create a new immutable planned task."""
        return self.ledger.create(name, provider)

    def start(self, task_id: str) -> ExecutionHandle:
        """Move a task to running and allocate its next attempt."""
        task = self.ledger.transition(task_id, TaskState.RUNNING)
        attempt = self.ledger.start_attempt(task_id)
        return ExecutionHandle(task_id=task_id, attempt=attempt.attempt, provider=task.provider)

    def succeed(self, task_id: str) -> Task:
        """Mark a running task successful after external verification."""
        return self.ledger.transition(task_id, TaskState.SUCCEEDED)

    def fail(self, task_id: str) -> Task:
        """Mark a running task failed after external verification."""
        return self.ledger.transition(task_id, TaskState.FAILED)

    def cancel(self, task_id: str) -> Task:
        """Cancel a planned or running task."""
        return self.ledger.transition(task_id, TaskState.CANCELLED)
