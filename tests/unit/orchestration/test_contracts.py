from datetime import datetime, timezone

import pytest

from quantlab.orchestration.contracts import (
    ArtifactRef,
    AgentProvider,
    Task,
    TaskState,
    transition,
)


def test_task_identity_is_stable_and_utc() -> None:
    task = Task.new("build", AgentProvider.AIDER, datetime(2026, 9, 17, tzinfo=timezone.utc))
    assert task.task_id
    assert task.created_at.tzinfo == timezone.utc
    assert task.state is TaskState.PLANNED


def test_artifact_ref_requires_sha256() -> None:
    with pytest.raises(ValueError):
        ArtifactRef(name="x", uri="file:///x", sha256="bad")


def test_valid_state_transitions() -> None:
    assert transition(TaskState.PLANNED, TaskState.RUNNING) is TaskState.RUNNING
    assert transition(TaskState.RUNNING, TaskState.SUCCEEDED) is TaskState.SUCCEEDED
    assert transition(TaskState.RUNNING, TaskState.FAILED) is TaskState.FAILED
    assert transition(TaskState.RUNNING, TaskState.CANCELLED) is TaskState.CANCELLED


def test_terminal_state_cannot_transition() -> None:
    with pytest.raises(ValueError):
        transition(TaskState.SUCCEEDED, TaskState.RUNNING)
