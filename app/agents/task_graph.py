"""
Task Graph – verwaltet Tasks und Abhängigkeiten.

Ermöglicht die Ausführung in korrekter Reihenfolge basierend auf Dependencies.
"""

from typing import Dict, List, Optional

from app.agents.task import Task, TaskStatus


class TaskGraph:
    """
    Verwaltet eine Menge von Tasks mit Abhängigkeiten.

    - add_task: Task hinzufügen
    - get_ready_tasks: Tasks ohne offene Dependencies
    - mark_completed: Task als erledigt markieren
    - get_next_tasks: Nächste ausführbare Tasks (priorisiert)
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._reverse_deps: Dict[str, List[str]] = {}  # task_id -> [tasks that depend on it]

    def add_task(self, task: Task) -> None:
        """Fügt einen Task hinzu und aktualisiert die Abhängigkeits-Indizes."""
        self._tasks[task.id] = task
        for dep_id in task.dependencies:
            if dep_id not in self._reverse_deps:
                self._reverse_deps[dep_id] = []
            if task.id not in self._reverse_deps[dep_id]:
                self._reverse_deps[dep_id].append(task.id)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Liefert einen Task nach ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Liefert alle Tasks."""
        return list(self._tasks.values())

    def get_ready_tasks(self) -> List[Task]:
        """
        Liefert Tasks, die bereit zur Ausführung sind.

        Ein Task ist bereit, wenn:
        - Status PENDING
        - Alle Dependencies sind COMPLETED
        """
        ready = []
        for task in self._tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            if self._all_dependencies_completed(task):
                ready.append(task)
        return ready

    def _all_dependencies_completed(self, task: Task) -> bool:
        """Prüft, ob alle Dependencies des Tasks abgeschlossen sind."""
        for dep_id in task.dependencies:
            dep = self._tasks.get(dep_id)
            if dep is None:
                continue  # Unbekannte Dependency ignorieren oder als erledigt ansehen
            if not dep.is_terminal or dep.status != TaskStatus.COMPLETED:
                return False
        return True

    def mark_completed(self, task_id: str, output: Optional[str] = None) -> bool:
        """
        Markiert einen Task als abgeschlossen.

        Returns:
            True wenn der Task existierte und aktualisiert wurde.
        """
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = TaskStatus.COMPLETED
        if output is not None:
            task.output = output
        task.touch()
        return True

    def mark_failed(self, task_id: str, error: Optional[str] = None) -> bool:
        """Markiert einen Task als fehlgeschlagen."""
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = TaskStatus.FAILED
        task.error = error
        task.touch()
        return True

    def mark_running(self, task_id: str) -> bool:
        """Markiert einen Task als laufend."""
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = TaskStatus.RUNNING
        task.touch()
        return True

    def get_next_tasks(self, limit: int = 5) -> List[Task]:
        """
        Liefert die nächsten ausführbaren Tasks, priorisiert.

        Sortierung: höhere priority zuerst, dann nach created_at.
        """
        ready = self.get_ready_tasks()
        sorted_tasks = sorted(
            ready,
            key=lambda t: (-t.priority, t.created_at or ""),
        )
        return sorted_tasks[:limit]

    def is_complete(self) -> bool:
        """True wenn alle Tasks in einem terminalen Status sind."""
        return all(t.is_terminal for t in self._tasks.values())

    def get_dependent_tasks(self, task_id: str) -> List[Task]:
        """Liefert alle Tasks, die von diesem Task abhängen."""
        dep_ids = self._reverse_deps.get(task_id, [])
        return [self._tasks[tid] for tid in dep_ids if tid in self._tasks]

    def clear(self) -> None:
        """Löscht alle Tasks."""
        self._tasks.clear()
        self._reverse_deps.clear()
