import pytest

from quantlab.orchestration.contracts import AgentProvider, TaskState
from quantlab.orchestration.ledger import TaskLedger


def test_create_and_transition(tmp_path) -> None:
    ledger = TaskLedger(tmp_path / "control.db")
    task = ledger.create("research", AgentProvider.GPT)
    assert task.state is TaskState.PLANNED
    updated = ledger.transition(task.task_id, TaskState.RUNNING)
    assert updated.state is TaskState.RUNNING


def test_illegal_transition_is_rejected(tmp_path) -> None:
    ledger = TaskLedger(tmp_path / "control.db")
    task = ledger.create("research", AgentProvider.GPT)
    ledger.transition(task.task_id, TaskState.RUNNING)
    ledger.transition(task.task_id, TaskState.SUCCEEDED)
    with pytest.raises(ValueError):
        ledger.transition(task.task_id, TaskState.RUNNING)


def test_attempt_history_is_monotonic(tmp_path) -> None:
    ledger = TaskLedger(tmp_path / "control.db")
    task = ledger.create("research", AgentProvider.CLAUDE)
    ledger.start_attempt(task.task_id)
    ledger.start_attempt(task.task_id)
    assert [a.attempt for a in ledger.attempts(task.task_id)] == [1, 2]


def test_unknown_task_is_rejected(tmp_path) -> None:
    ledger = TaskLedger(tmp_path / "control.db")
    with pytest.raises(KeyError):
        ledger.transition("missing", TaskState.RUNNING)


def test_reopen_returns_same_task(tmp_path) -> None:
    ledger = TaskLedger(tmp_path / "control.db")
    task = ledger.create("research", AgentProvider.GPT)
    loaded = ledger.get(task.task_id)
    assert loaded.task_id == task.task_id
