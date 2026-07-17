from datetime import date, timedelta

import storage
import task_manager


def test_overdue_tasks_are_detected(monkeypatch, tmp_path):
    task_file = tmp_path / "tasks.json"
    monkeypatch.setattr(task_manager, "TASK_FILE", str(task_file))

    task_manager.add_task(1, "Pay bills", "Pay rent", (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "High")
    task_manager.add_task(1, "Buy milk", "Groceries", (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"), "Low")

    overdue = task_manager.get_overdue_tasks(1)

    assert len(overdue) == 1
    assert overdue[0].title == "Pay bills"


def test_session_helpers_round_trip(monkeypatch, tmp_path):
    session_file = tmp_path / "session.json"
    monkeypatch.setattr(storage, "SESSION_FILE", str(session_file))

    storage.save_session({"user_id": 7, "username": "Ada"})
    assert storage.load_session() == {"user_id": 7, "username": "Ada"}

    storage.clear_session()
    assert storage.load_session() is None
