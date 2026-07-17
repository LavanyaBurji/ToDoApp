from task_manager import (
    add_task,
    get_all_tasks,
    update_task,
    delete_task,
    mark_completed,
    search_tasks,
    filter_by_status,
    filter_by_priority,
    sort_by_due_date,
    sort_by_priority,
    get_statistics,
    display_tasks
)

from utils import (
    get_integer,
    validate_title,
    validate_description,
    validate_due_date,
    validate_priority,
    confirm,
    print_heading,
    pause
)


# =====================================================
# TEMPORARY LOGIN
# Replace this after Person A integration
# =====================================================

CURRENT_USER_ID = 1


# =====================================================
# ADD TASK MENU
# =====================================================

def add_task_menu():

    print_heading("ADD NEW TASK")

    try:

        title = validate_title(
            input("Title: ")
        )

        description = validate_description(
            input("Description: ")
        )

        due_date = validate_due_date(
            input("Due Date (YYYY-MM-DD): ")
        )

        priority = validate_priority(
            input("Priority (High/Medium/Low): ")
        )


        task = add_task(
            CURRENT_USER_ID,
            title,
            description,
            due_date,
            priority
        )

        print(
            "\nTask added successfully!"
        )

        print(
            f"Task ID: {task.task_id}"
        )

    except ValueError as error:

        print(
            f"\nError: {error}"
        )

    pause()



# =====================================================
# VIEW TASKS
# =====================================================

def view_tasks_menu():

    print_heading("YOUR TASKS")

    tasks = get_all_tasks(
        CURRENT_USER_ID
    )

    display_tasks(tasks)

    pause()



# =====================================================
# UPDATE TASK
# =====================================================

def update_task_menu():

    print_heading("UPDATE TASK")

    task_id = get_integer(
        "Enter Task ID: "
    )


    try:

        title = validate_title(
            input("New Title: ")
        )

        description = validate_description(
            input("New Description: ")
        )

        due_date = validate_due_date(
            input("New Due Date: ")
        )

        priority = validate_priority(
            input("New Priority: ")
        )


        result = update_task(
            CURRENT_USER_ID,
            task_id,
            title,
            description,
            due_date,
            priority
        )


        if result:

            print(
                "\nTask updated successfully!"
            )

        else:

            print(
                "\nTask not found."
            )


    except ValueError as error:

        print(
            f"\nError: {error}"
        )


    pause()



# =====================================================
# DELETE TASK
# =====================================================

def delete_task_menu():

    print_heading("DELETE TASK")


    task_id = get_integer(
        "Enter Task ID: "
    )


    if confirm(
        "Are you sure you want to delete?"
    ):


        result = delete_task(
            CURRENT_USER_ID,
            task_id
        )


        if result:

            print(
                "\nTask deleted successfully!"
            )

        else:

            print(
                "\nTask not found."
            )


    pause()



# =====================================================
# COMPLETE TASK
# =====================================================

def complete_task_menu():

    print_heading(
        "MARK TASK COMPLETE"
    )


    task_id = get_integer(
        "Enter Task ID: "
    )


    result = mark_completed(
        CURRENT_USER_ID,
        task_id
    )


    if result:

        print(
            "\nTask completed!"
        )

    else:

        print(
            "\nTask not found."
        )


    pause()



# =====================================================
# SEARCH TASK
# =====================================================

def search_task_menu():

    print_heading(
        "SEARCH TASK"
    )


    keyword = input(
        "Enter keyword: "
    )


    results = search_tasks(
        CURRENT_USER_ID,
        keyword
    )


    display_tasks(results)

    pause()



# =====================================================
# FILTER MENU
# =====================================================

def filter_menu():

    print_heading(
        "FILTER TASKS"
    )


    print(
        "1. Filter by Status"
    )

    print(
        "2. Filter by Priority"
    )


    choice = input(
        "Choice: "
    )


    if choice == "1":

        status = input(
            "Status (Pending/Completed): "
        )


        tasks = filter_by_status(
            CURRENT_USER_ID,
            status
        )


    elif choice == "2":

        priority = input(
            "Priority (High/Medium/Low): "
        )


        tasks = filter_by_priority(
            CURRENT_USER_ID,
            priority
        )


    else:

        print(
            "Invalid choice."
        )

        pause()

        return


    display_tasks(tasks)

    pause()



# =====================================================
# SORT MENU
# =====================================================

def sort_menu():

    print_heading(
        "SORT TASKS"
    )


    print(
        "1. Sort by Due Date"
    )

    print(
        "2. Sort by Priority"
    )


    choice = input(
        "Choice: "
    )


    if choice == "1":

        tasks = sort_by_due_date(
            CURRENT_USER_ID
        )


    elif choice == "2":

        tasks = sort_by_priority(
            CURRENT_USER_ID
        )


    else:

        print(
            "Invalid choice."
        )

        pause()

        return


    display_tasks(tasks)

    pause()



# =====================================================
# STATISTICS
# =====================================================

def statistics_menu():

    print_heading(
        "TASK STATISTICS"
    )


    stats = get_statistics(
        CURRENT_USER_ID
    )


    print(
        f"""
Total Tasks       : {stats['total']}
Completed         : {stats['completed']}
Pending           : {stats['pending']}
High Priority     : {stats['high_priority']}
Medium Priority   : {stats['medium_priority']}
Low Priority      : {stats['low_priority']}
Completion Rate   : {stats['completion_rate']}%
"""
    )

    pause()



# =====================================================
# MAIN MENU
# =====================================================

def main():

    while True:

        print_heading(
            "TASK MANAGEMENT SYSTEM"
        )


        print(
            """
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Completed
6. Search Tasks
7. Filter Tasks
8. Sort Tasks
9. Statistics
0. Exit
"""
        )


        choice = input(
            "Enter choice: "
        )


        if choice == "1":

            add_task_menu()


        elif choice == "2":

            view_tasks_menu()


        elif choice == "3":

            update_task_menu()


        elif choice == "4":

            delete_task_menu()


        elif choice == "5":

            complete_task_menu()


        elif choice == "6":

            search_task_menu()


        elif choice == "7":

            filter_menu()


        elif choice == "8":

            sort_menu()


        elif choice == "9":

            statistics_menu()


        elif choice == "0":

            print(
                "\nGoodbye!"
            )

            break


        else:

            print(
                "\nInvalid option."
            )



if __name__ == "__main__":

    main()