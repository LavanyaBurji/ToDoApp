from auth import register, login, logout
from storage import load_session, save_session, clear_session
from task_manager import (
    add_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    mark_completed,
    search_tasks,
    filter_by_status,
    filter_by_priority,
    sort_by_due_date,
    sort_by_priority,
    display_tasks,
    get_statistics,
    get_task_summary,
    get_overdue_tasks,
)


def show_dashboard(user):
    stats = get_statistics(user["user_id"])
    print(f"\nWelcome back, {user['username']}!")
    print("===== DASHBOARD =====")
    print(f"Total tasks: {stats['total']}")
    print(f"Completed: {stats['completed']}")
    print(f"Pending: {stats['pending']}")
    print(f"High priority: {stats['high_priority']}")
    print(f"Completion rate: {stats['completion_rate']}%")

    summary = get_task_summary(user["user_id"])
    print("\nTask summary")
    print(f"Pending: {summary['pending']}")
    print(f"Overdue: {summary['overdue']}")

    overdue = get_overdue_tasks(user["user_id"])
    if overdue:
        print("\nOverdue tasks:")
        for task in overdue:
            print(f"- {task.title} (due {task.due_date})")

current_user = None


def validate_current_user(user):
    if not user:
        return False

    saved_session = load_session()
    if not saved_session or saved_session.get("user_id") != user.get("user_id"):
        return False

    return True


def task_menu():
    global current_user
    if not current_user:
        print("Please log in first.")
        return

    if not validate_current_user(current_user):
        print("Your session is invalid or has been cleared. Please log in again.")
        current_user = None
        clear_session()
        return

    show_dashboard(current_user)

    while True:
        if not validate_current_user(current_user):
            print("Your session is invalid or has been cleared. Please log in again.")
            current_user = None
            clear_session()
            return

        print("\n===== TASK MENU =====")
        print("1. View tasks")
        print("2. Add task")
        print("3. Update task")
        print("4. Delete task")
        print("5. Mark complete")
        print("6. Search tasks")
        print("7. Filter by status")
        print("8. Filter by priority")
        print("9. Sort by due date")
        print("10. Sort by priority")
        print("11. Show statistics")
        print("12. Back")

        choice = input("Choose: ").strip()

        if choice == "1":
            tasks = get_all_tasks(current_user["user_id"])
            display_tasks(tasks)
        elif choice == "2":
            title = input("Title: ").strip()
            description = input("Description: ").strip()
            due_date = input("Due date (YYYY-MM-DD): ").strip()
            priority = input("Priority (High/Medium/Low): ").strip()
            try:
                task = add_task(current_user["user_id"], title, description, due_date, priority)
                print(f"Task added: {task.title}")
            except ValueError as exc:
                print(f"Unable to add task: {exc}")
        elif choice == "3":
            try:
                task_id = int(input("Task ID: ").strip())
            except ValueError:
                print("Please enter a valid task ID.")
                continue
            title = input("New title: ").strip()
            description = input("New description: ").strip()
            due_date = input("New due date (YYYY-MM-DD): ").strip()
            priority = input("New priority (High/Medium/Low): ").strip()
            try:
                if update_task(current_user["user_id"], task_id, title, description, due_date, priority):
                    print("Task updated.")
                else:
                    print("Task not found.")
            except Exception as exc:
                print(f"Error updating task: {exc}")
        elif choice == "4":
            try:
                task_id = int(input("Task ID: ").strip())
            except ValueError:
                print("Please enter a valid task ID.")
                continue
            try:
                if delete_task(current_user["user_id"], task_id):
                    print("Task deleted.")
                else:
                    print("Task not found.")
            except Exception as exc:
                print(f"Error deleting task: {exc}")
        elif choice == "5":
            try:
                task_id = int(input("Task ID: ").strip())
            except ValueError:
                print("Please enter a valid task ID.")
                continue
            try:
                if mark_completed(current_user["user_id"], task_id):
                    print("Task marked complete.")
                else:
                    print("Task not found.")
            except Exception as exc:
                print(f"Error marking task complete: {exc}")
        elif choice == "6":
            keyword = input("Search keyword: ").strip()
            display_tasks(search_tasks(current_user["user_id"], keyword))
        elif choice == "7":
            status = input("Status: ").strip()
            display_tasks(filter_by_status(current_user["user_id"], status))
        elif choice == "8":
            priority = input("Priority: ").strip()
            display_tasks(filter_by_priority(current_user["user_id"], priority))
        elif choice == "9":
            display_tasks(sort_by_due_date(current_user["user_id"], True))
        elif choice == "10":
            display_tasks(sort_by_priority(current_user["user_id"]))
        elif choice == "11":
            stats = get_statistics(current_user["user_id"])
            print(stats)
        elif choice == "12":
            break
        else:
            print("Invalid option.")


saved_session = None
try:
    saved_session = load_session()
except Exception as exc:
    print("Warning: Could not restore session from storage.")
    print(f"Reason: {exc}")

if saved_session:
    current_user = saved_session
    print(f"Welcome back, {current_user['username']}!")
    show_dashboard(current_user)

while True:
    print("\n===== TODO APP =====")
    print("1. Register")
    print("2. Login")
    print("3. Logout")
    print("4. Task Menu")
    print("5. Exit")

    choice = input("Choose: ").strip()

    if choice == "1":
        register()
    elif choice == "2":
        current_user = login()
        if current_user:
            try:
                save_session(current_user)
            except Exception as exc:
                print("Warning: failed to persist login session.")
                print(f"Reason: {exc}")
            show_dashboard(current_user)
    elif choice == "3":
        current_user = logout()
        clear_session()
        current_user = None
    elif choice == "4":
        task_menu()
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid option.")