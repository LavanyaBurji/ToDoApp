import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import task_manager
from models import Task
from config import TASKS_FILE


def test_save_tasks_creates_backup(tmp_path, monkeypatch):
    custom_tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(task_manager, "TASKS_FILE", str(custom_tasks_file))
    monkeypatch.setattr(task_manager, "_ensure_database_dir", lambda: os.makedirs(tmp_path, exist_ok=True))

    tasks = [Task(task_id=1, user_id=1, title="Test", description="Desc", due_date="2025-01-01", priority="Medium")]
    task_manager.save_tasks(tasks)

    assert custom_tasks_file.exists()

    # Create a second save so a backup is generated
    tasks[0].title = "Test Updated"
    task_manager.save_tasks(tasks)

    backups = list(tmp_path.glob("tasks.json.*.bak"))
    assert len(backups) >= 1


def test_restore_deleted_task_from_backup(tmp_path, monkeypatch):
    custom_tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(task_manager, "TASKS_FILE", str(custom_tasks_file))
    monkeypatch.setattr(task_manager, "_ensure_database_dir", lambda: os.makedirs(tmp_path, exist_ok=True))

    tasks = [
        Task(task_id=1, user_id=1, title="Restore Task", description="Desc", due_date="2025-01-01", priority="High")
    ]
    task_manager.save_tasks(tasks)
    tasks[0].title = "Restore Task Updated"
    task_manager.save_tasks(tasks)

    assert custom_tasks_file.exists()

    # Simulate accidental deletion
    custom_tasks_file.unlink()
    assert not custom_tasks_file.exists()

    restored = task_manager.restore_tasks_from_backup()
    assert restored is True
    assert custom_tasks_file.exists()

    with open(custom_tasks_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data[0]["title"] == "Restore Task"


def test_restore_deleted_task_by_id(tmp_path, monkeypatch):
    custom_tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(task_manager, "TASKS_FILE", str(custom_tasks_file))
    monkeypatch.setattr(task_manager, "_ensure_database_dir", lambda: os.makedirs(tmp_path, exist_ok=True))

    tasks = [
        Task(task_id=1, user_id=1, title="Restore Me", description="Desc", due_date="2025-01-01", priority="Low")
    ]
    task_manager.save_tasks(tasks)
    tasks[0].title = "Restore Me Updated"
    task_manager.save_tasks(tasks)

    custom_tasks_file.unlink()
    restored = task_manager.restore_deleted_task(user_id=1, task_id=1)

    assert restored is True
    assert custom_tasks_file.exists()

    with open(custom_tasks_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data[0]["title"] == "Restore Me"


def _run_subprocess_save(custom_tasks_file, title):
    script = f"""
import os
import sys
from pathlib import Path
import json

ROOT = Path(r'{Path(__file__).resolve().parents[1]}')
sys.path.insert(0, str(ROOT))

import task_manager
from models import Task

TASKS_FILE = r'{str(custom_tasks_file)}'
task_manager.TASKS_FILE = TASKS_FILE

task_manager._ensure_database_dir = lambda: os.makedirs(Path(TASKS_FILE).parent, exist_ok=True)

new_task = Task(task_id=1, user_id=1, title={json.dumps(title)}, description='Desc', due_date='2025-01-01', priority='Low')
task_manager.save_tasks([new_task])
"""
    subprocess.run([sys.executable, "-c", script], check=True)


def test_concurrent_save_tasks_does_not_corrupt(tmp_path):
    custom_tasks_file = tmp_path / "tasks.json"
    titles = [f"Concurrent {i}" for i in range(3)]

    processes = []
    for title in titles:
        process = subprocess.Popen([sys.executable, "-c", f"import os, sys; from pathlib import Path; import json; ROOT = Path(r'{Path(__file__).resolve().parents[1]}'); sys.path.insert(0, str(ROOT)); import task_manager; from models import Task; TASKS_FILE = r'{str(custom_tasks_file)}'; task_manager.TASKS_FILE = TASKS_FILE; task_manager._ensure_database_dir = lambda: os.makedirs(Path(TASKS_FILE).parent, exist_ok=True); task = Task(task_id=1, user_id=1, title={json.dumps(title)}, description='Desc', due_date='2025-01-01', priority='Low'); task_manager.save_tasks([task])"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append((process, title))

    for process, title in processes:
        stdout, stderr = process.communicate(timeout=15)
        assert process.returncode == 0, f"Subprocess failed for {title}: {stderr.decode('utf-8')}"

    with open(custom_tasks_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, list)
    assert data[0]["title"] in titles
