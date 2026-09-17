import pytest

from quantlab.orchestration.contracts import AgentProvider, TaskState
from quantlab.orchestration.orchestrator import ControlPlane


def test_control_plane_creates_and_starts_task(tmp_path) -> None:
    cp = ControlPlane(tmp_path / "control.db")
    task = cp.plan("backtest", AgentProvider.COLAB)
    handle = cp.start(task.task_id)
    assert handle.task_id == task.task_id
    assert handle.attempt == 1
    assert cp.ledger.get(task.task_id).state is TaskState.RUNNING


def test_control_plane_requires_verification_before_success(tmp_path) -> None:
    cp = ControlPlane(tmp_path / "control.db")
    task = cp.plan("backtest", AgentProvider.COLAB)
    with pytest.raises(ValueError):
        cp.succeed(task.task_id)


def test_control_plane_failure_is_terminal(tmp_path) -> None:
    cp = ControlPlane(tmp_path / "control.db")
    task = cp.plan("backtest", AgentProvider.COLAB)
    cp.start(task.task_id)
    cp.fail(task.task_id)
    with pytest.raises(ValueError):
        cp.start(task.task_id)


def test_control_plane_cancellation_from_planned(tmp_path) -> None:
    cp = ControlPlane(tmp_path / "control.db")
    task = cp.plan("backtest", AgentProvider.COLAB)
    assert cp.cancel(task.task_id).state is TaskState.CANCELLED


def test_attempts_are_not_reused(tmp_path) -> None:
    cp = ControlPlane(tmp_path / "control.db")
    task = cp.plan("review", AgentProvider.CLAUDE)
    cp.start(task.task_id)
    cp.fail(task.task_id)
    with pytest.raises(ValueError):
        cp.start(task.task_id)
