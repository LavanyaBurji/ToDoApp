import json
import os
from datetime import datetime

from models import Task
from utils import (
    validate_title,
    validate_description,
    validate_due_date,
    validate_priority,
)

TASK_FILE = os.path.join("database", "tasks.json")


# =====================================================
# STORAGE FUNCTIONS
# =====================================================

def load_tasks():
    """
    Loads all tasks from tasks.json
    Returns a list of Task objects.
    """

    try:

        with open(TASK_FILE, "r") as file:

            data = json.load(file)

            return [
                Task.from_dict(task)
                for task in data
            ]

    except (FileNotFoundError, json.JSONDecodeError):

        return []


def save_tasks(tasks):
    """
    Saves Task objects to JSON.
    """

    with open(TASK_FILE, "w") as file:

        json.dump(

            [task.to_dict() for task in tasks],

            file,

            indent=4

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

    title = validate_title(title)

    description = validate_description(description)

    due_date = validate_due_date(due_date)

    priority = validate_priority(priority)

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

    title = validate_title(title)

    description = validate_description(description)

    due_date = validate_due_date(due_date)

    priority = validate_priority(priority)

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