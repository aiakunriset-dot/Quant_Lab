from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any
from uuid import uuid4


class AgentProvider(StrEnum):
    """Supported control-plane execution providers."""

    GPT = "gpt"
    CLAUDE = "claude"
    AIDER = "aider"
    COLAB = "colab"
    GITHUB = "github"
    GDRIVE = "gdrive"


class TaskState(StrEnum):
    """Monotonic orchestration task states."""

    PLANNED = "planned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


_TERMINAL = {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.CANCELLED}
_ALLOWED = {
    TaskState.PLANNED: {TaskState.RUNNING, TaskState.CANCELLED},
    TaskState.RUNNING: {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.SUCCEEDED: set(),
    TaskState.FAILED: set(),
    TaskState.CANCELLED: set(),
}


def transition(current: TaskState, target: TaskState) -> TaskState:
    """Validate and return a legal monotonic state transition."""
    if target not in _ALLOWED[current]:
        raise ValueError(f"illegal task transition: {current.value} -> {target.value}")
    return target


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    """Immutable reference to a content-addressed artifact."""

    name: str
    uri: str
    sha256: str
    producer: str = "unknown"
    task_id: str | None = None
    schema_version: str = "1"

    def __post_init__(self) -> None:
        """Validate artifact identity fields."""
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256.lower()):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if not self.name or not self.uri:
            raise ValueError("artifact name and uri are required")


@dataclass(frozen=True, slots=True)
class Task:
    """Immutable task identity and current state."""

    task_id: str
    name: str
    provider: AgentProvider
    created_at: datetime
    state: TaskState = TaskState.PLANNED
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def new(cls, name: str, provider: AgentProvider, created_at: datetime | None = None) -> "Task":
        """Create a task with a UUID and normalized UTC creation time."""
        now = created_at or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        now = now.astimezone(timezone.utc)
        return cls(task_id=str(uuid4()), name=name, provider=provider, created_at=now)

    def to_json(self) -> str:
        """Serialize the task deterministically without secrets."""
        payload = {
            "task_id": self.task_id,
            "name": self.name,
            "provider": self.provider.value,
            "created_at": self.created_at.isoformat(),
            "state": self.state.value,
            "metadata": self.metadata,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def fingerprint(self) -> str:
        """Return the deterministic SHA-256 fingerprint of task identity."""
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()
