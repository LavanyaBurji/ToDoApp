import json
import logging
import os
import shutil
import tempfile
import time
from datetime import datetime

from config import TASKS_FILE
from models import Task
from utils import (
    validate_title,
    validate_description,
    validate_due_date,
    validate_priority,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# =====================================================
# STORAGE HELPERS
# =====================================================

def _ensure_database_dir():
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)


def _backup_file(path, keep=5):
    if not os.path.exists(path):
        return

    directory = os.path.dirname(path)
    base = os.path.basename(path)
    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(directory, f"{base}.{timestamp}.bak")
    shutil.copy2(path, backup_path)

    backups = sorted(
        [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.startswith(base + ".") and f.endswith(".bak")
        ],
        reverse=True,
    )
    for old_backup in backups[keep:]:
        try:
            os.remove(old_backup)
        except OSError:
            pass


def _restore_from_backup(path):
    directory = os.path.dirname(path)
    base = os.path.basename(path)
    candidates = sorted(
        [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.startswith(base + ".") and f.endswith(".bak")
        ],
        reverse=True,
    )
    if not candidates:
        return False

    for backup_path in candidates:
        try:
            shutil.copy2(backup_path, path)
            logger.info("Restored %s from backup %s", path, backup_path)
            return True
        except OSError as exc:
            logger.error("Failed to restore %s from backup %s: %s", path, backup_path, exc)
            continue
    return False


def _find_latest_backup(path):
    directory = os.path.dirname(path)
    base = os.path.basename(path)
    backups = sorted(
        [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.startswith(base + ".") and f.endswith(".bak")
        ],
        reverse=True,
    )
    return backups[0] if backups else None


def restore_tasks_from_backup():
    return _restore_from_backup(TASKS_FILE)


def restore_deleted_task(user_id, task_id):
    current_tasks = load_tasks()
    if any(task.task_id == task_id and task.user_id == user_id for task in current_tasks):
        return True

    backup_path = _find_latest_backup(TASKS_FILE)
    if not backup_path:
        return False

    try:
        with open(backup_path, "r", encoding="utf-8") as file:
            backup_tasks = [Task.from_dict(task) for task in json.load(file)]
    except (OSError, json.JSONDecodeError):
        return False

    if not any(task.task_id == task_id and task.user_id == user_id for task in backup_tasks):
        return False

    return _restore_from_backup(TASKS_FILE)


def _atomic_write(path, data):
    _ensure_database_dir()
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8") as tmp:
        json.dump(data, tmp, indent=4)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = tmp.name
    os.replace(temp_path, path)


def _handle_corrupt_file(path):
    try:
        corrupt_path = f"{path}.corrupt"
        if os.path.exists(corrupt_path):
            os.remove(corrupt_path)
        os.replace(path, corrupt_path)
        logger.warning("Backed up corrupt JSON file to %s", corrupt_path)
    except OSError as exc:
        logger.error("Unable to backup corrupt JSON file %s: %s", path, exc)


def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        if _restore_from_backup(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception:
                return default
        return default
    except json.JSONDecodeError:
        logger.warning("JSON decode failed for %s", path)
        _handle_corrupt_file(path)
        if _restore_from_backup(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception:
                return default
        return default
    except OSError as exc:
        logger.error("Unable to read %s: %s", path, exc)
        return default


# =====================================================
# STORAGE FUNCTIONS
# =====================================================

def load_tasks():
    """
    Loads all tasks from tasks.json
    Returns a list of Task objects.
    """

    tasks_data = _read_json(TASKS_FILE, [])
    return [Task.from_dict(task) for task in tasks_data]


def save_tasks(tasks):
    """
    Saves Task objects to JSON.
    """

    _backup_file(TASKS_FILE)
    _atomic_write(
        TASKS_FILE,
        [task.to_dict() for task in tasks],
    )


# =====================================================
# ID GENERATION
# =====================================================

def generate_task_id(tasks):

    if not tasks:
        return 1

    return max(task.task_id for task in tasks) + 1


# =====================================================
# CREATE
# =====================================================

def add_task(
    user_id,
    title,
    description,
    due_date,
    priority
):

    tasks = load_tasks()

    valid_title, title = validate_title(title)
    if not valid_title:
        raise ValueError(title)

    valid_description, description = validate_description(description)
    if not valid_description:
        raise ValueError(description)

    valid_due_date, due_date = validate_due_date(due_date)
    if not valid_due_date:
        raise ValueError(due_date)

    valid_priority, priority = validate_priority(priority)
    if not valid_priority:
        raise ValueError(priority)

    existing_titles = {task.title.lower() for task in tasks if task.user_id == user_id}
    if title.lower() in existing_titles:
        raise ValueError("A task with this title already exists.")

    task = Task(

        task_id=generate_task_id(tasks),

        user_id=user_id,

        title=title,

        description=description,

        due_date=due_date,

        priority=priority,

        status="Pending"

    )

    tasks.append(task)

    save_tasks(tasks)

    return task


# =====================================================
# READ
# =====================================================

def get_all_tasks(user_id):

    tasks = load_tasks()

    return [

        task

        for task in tasks

        if task.user_id == user_id

    ]


def get_task_by_id(
    user_id,
    task_id
):

    tasks = load_tasks()

    for task in tasks:

        if (

            task.task_id == task_id

            and

            task.user_id == user_id

        ):

            return task

    return None


# =====================================================
# UPDATE
# =====================================================

def update_task(

    user_id,

    task_id,

    title,

    description,

    due_date,

    priority

):

    tasks = load_tasks()

    valid_title, title = validate_title(title)
    if not valid_title:
        return False

    valid_description, description = validate_description(description)
    if not valid_description:
        return False

    valid_due_date, due_date = validate_due_date(due_date)
    if not valid_due_date:
        return False

    valid_priority, priority = validate_priority(priority)
    if not valid_priority:
        return False

    for task in tasks:

        if (

            task.task_id == task_id

            and

            task.user_id == user_id

        ):

            task.update(

                title,

                description,

                due_date,

                priority

            )

            save_tasks(tasks)

            return True

    return False


# =====================================================
# DELETE
# =====================================================

def delete_task(
    user_id,
    task_id
):

    tasks = load_tasks()

    for task in tasks:

        if (

            task.task_id == task_id

            and

            task.user_id == user_id

        ):

            tasks.remove(task)

            save_tasks(tasks)

            return True

    return False


# =====================================================
# MARK COMPLETE
# =====================================================

def mark_completed(
    user_id,
    task_id
):

    tasks = load_tasks()

    for task in tasks:

        if (

            task.task_id == task_id

            and

            task.user_id == user_id

        ):

            task.mark_completed()

            save_tasks(tasks)

            return True

    return False


# =====================================================
# SEARCH
# =====================================================

def search_tasks(
    user_id,
    keyword
):

    keyword = keyword.lower()

    tasks = get_all_tasks(user_id)

    return [

        task

        for task in tasks

        if (

            keyword in task.title.lower()

            or

            keyword in task.description.lower()

        )

    ]


# =====================================================
# FILTER
# =====================================================

def filter_by_status(
    user_id,
    status
):

    status = status.capitalize()

    tasks = get_all_tasks(user_id)

    return [

        task

        for task in tasks

        if task.status == status

    ]


def filter_by_priority(
    user_id,
    priority
):

    priority = priority.capitalize()

    tasks = get_all_tasks(user_id)

    return [

        task

        for task in tasks

        if task.priority == priority

    ]
# =====================================================
# SORTING
# =====================================================

def sort_by_due_date(user_id, ascending=True):
    """
    Returns tasks sorted by due date.
    """

    tasks = get_all_tasks(user_id)

    return sorted(
        tasks,
        key=lambda task: datetime.strptime(
            task.due_date,
            "%Y-%m-%d"
        ),
        reverse=not ascending
    )


def sort_by_priority(user_id):
    """
    Sort tasks by priority:
    High -> Medium -> Low
    """

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    tasks = get_all_tasks(user_id)

    return sorted(
        tasks,
        key=lambda task: priority_order.get(
            task.priority,
            4
        )
    )


# =====================================================
# STATISTICS
# =====================================================

def get_statistics(user_id):
    """
    Returns task statistics.
    """

    tasks = get_all_tasks(user_id)

    total = len(tasks)

    completed = sum(
        1
        for task in tasks
        if task.status == "Completed"
    )

    pending = total - completed

    high = sum(
        1
        for task in tasks
        if task.priority == "High"
    )

    medium = sum(
        1
        for task in tasks
        if task.priority == "Medium"
    )

    low = sum(
        1
        for task in tasks
        if task.priority == "Low"
    )

    completion_rate = (
        round((completed / total) * 100, 2)
        if total > 0
        else 0
    )

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "high_priority": high,
        "medium_priority": medium,
        "low_priority": low,
        "completion_rate": completion_rate
    }


def get_overdue_tasks(user_id):
    today = datetime.today().date()
    tasks = get_all_tasks(user_id)
    overdue = []
    for task in tasks:
        if task.status != "Completed":
            due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            if due_date < today:
                overdue.append(task)
    return overdue


def get_task_summary(user_id):
    tasks = get_all_tasks(user_id)
    overdue = get_overdue_tasks(user_id)
    return {
        "total": len(tasks),
        "completed": sum(1 for task in tasks if task.status == "Completed"),
        "pending": sum(1 for task in tasks if task.status != "Completed"),
        "overdue": len(overdue),
    }


# =====================================================
# DISPLAY FUNCTIONS
# =====================================================

def display_task(task):
    """
    Displays a single task.
    """

    print("-" * 60)

    print(f"Task ID     : {task.task_id}")
    print(f"Title       : {task.title}")
    print(f"Description : {task.description}")
    print(f"Due Date    : {task.due_date}")
    print(f"Priority    : {task.priority}")
    print(f"Status      : {task.status}")

    print("-" * 60)


def display_tasks(tasks):
    """
    Displays multiple tasks.
    """

    if not tasks:

        print("\nNo tasks found.\n")

        return

    print("\n" + "=" * 75)

    print(
        f"{'ID':<5}"
        f"{'TITLE':<25}"
        f"{'PRIORITY':<12}"
        f"{'STATUS':<12}"
        f"{'DUE DATE':<15}"
    )

    print("=" * 75)

    for task in tasks:

        print(
            f"{task.task_id:<5}"
            f"{task.title[:24]:<25}"
            f"{task.priority:<12}"
            f"{task.status:<12}"
            f"{task.due_date:<15}"
        )

    print("=" * 75)


# =====================================================
# EXISTENCE CHECKS
# =====================================================

def task_exists(user_id, task_id):
    """
    Returns True if the task exists.
    """

    return get_task_by_id(user_id, task_id) is not None


def total_tasks(user_id):
    """
    Returns total number of tasks.
    """

    return len(get_all_tasks(user_id))


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":

    USER_ID = 1

    add_task(
        USER_ID,
        "Complete Python Assignment",
        "Finish the Task Manager backend.",
        "2026-07-25",
        "High"
    )

    add_task(
        USER_ID,
        "Prepare Presentation",
        "Create project PPT.",
        "2026-07-22",
        "Medium"
    )

    print("\nALL TASKS")
    display_tasks(
        get_all_tasks(USER_ID)
    )

    print("\nSEARCH RESULTS")
    display_tasks(
        search_tasks(
            USER_ID,
            "python"
        )
    )

    print("\nSORTED BY DUE DATE")
    display_tasks(
        sort_by_due_date(USER_ID)
    )

    print("\nSORTED BY PRIORITY")
    display_tasks(
        sort_by_priority(USER_ID)
    )

    print("\nSTATISTICS")

    stats = get_statistics(USER_ID)

    print(f"Total Tasks       : {stats['total']}")
    print(f"Completed         : {stats['completed']}")
    print(f"Pending           : {stats['pending']}")
    print(f"High Priority     : {stats['high_priority']}")
    print(f"Medium Priority   : {stats['medium_priority']}")
    print(f"Low Priority      : {stats['low_priority']}")
    print(f"Completion Rate   : {stats['completion_rate']}%")