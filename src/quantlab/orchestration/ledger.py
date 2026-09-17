from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from quantlab.orchestration.contracts import AgentProvider, Task, TaskState, transition


@dataclass(frozen=True, slots=True)
class Attempt:
    """Immutable task execution attempt record."""

    task_id: str
    attempt: int
    started_at: datetime


class TaskLedger:
    """SQLite-backed task state and attempt ledger."""

    def __init__(self, database: Path) -> None:
        """Initialize the database and create required tables."""
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, name TEXT NOT NULL, provider TEXT NOT NULL, created_at TEXT NOT NULL, state TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS attempts (task_id TEXT NOT NULL, attempt INTEGER NOT NULL, started_at TEXT NOT NULL, PRIMARY KEY(task_id, attempt), FOREIGN KEY(task_id) REFERENCES tasks(task_id))"
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with foreign keys enabled."""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def create(self, name: str, provider: AgentProvider) -> Task:
        """Create and persist a planned task."""
        task = Task.new(name, provider)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO tasks(task_id,name,provider,created_at,state) VALUES(?,?,?,?,?)",
                (task.task_id, task.name, task.provider.value, task.created_at.isoformat(), task.state.value),
            )
        return task

    def get(self, task_id: str) -> Task:
        """Load a task by identity."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT task_id,name,provider,created_at,state FROM tasks WHERE task_id=?", (task_id,)
            ).fetchone()
        if row is None:
            raise KeyError(task_id)
        return Task(
            task_id=row[0],
            name=row[1],
            provider=AgentProvider(row[2]),
            created_at=datetime.fromisoformat(row[3]),
            state=TaskState(row[4]),
        )

    def transition(self, task_id: str, target: TaskState) -> Task:
        """Apply one legal state transition transactionally."""
        task = self.get(task_id)
        next_state = transition(task.state, target)
        with self._connect() as conn:
            conn.execute("UPDATE tasks SET state=? WHERE task_id=?", (next_state.value, task_id))
        return self.get(task_id)

    def start_attempt(self, task_id: str) -> Attempt:
        """Create the next monotonic attempt for a task."""
        self.get(task_id)
        now = datetime.now(timezone.utc)
        with self._connect() as conn:
            row = conn.execute("SELECT COALESCE(MAX(attempt),0)+1 FROM attempts WHERE task_id=?", (task_id,)).fetchone()
            number = int(row[0])
            conn.execute(
                "INSERT INTO attempts(task_id,attempt,started_at) VALUES(?,?,?)",
                (task_id, number, now.isoformat()),
            )
        return Attempt(task_id, number, now)

    def attempts(self, task_id: str) -> list[Attempt]:
        """Return attempts in chronological order."""
        self.get(task_id)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT task_id,attempt,started_at FROM attempts WHERE task_id=? ORDER BY attempt", (task_id,)
            ).fetchall()
        return [Attempt(r[0], r[1], datetime.fromisoformat(r[2])) for r in rows]
