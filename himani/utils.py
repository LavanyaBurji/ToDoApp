from datetime import datetime


VALID_PRIORITIES = ["High", "Medium", "Low"]
VALID_STATUS = ["Pending", "Completed"]


def validate_title(title):
    """
    Validate task title.
    """

    title = title.strip()

    if len(title) == 0:
        raise ValueError("Title cannot be empty.")

    if len(title) > 100:
        raise ValueError("Title cannot exceed 100 characters.")

    return title


def validate_description(description):
    """
    Validate description.
    """

    description = description.strip()

    if len(description) == 0:
        raise ValueError("Description cannot be empty.")

    if len(description) > 500:
        raise ValueError("Description cannot exceed 500 characters.")

    return description


def validate_priority(priority):
    """
    Validate task priority.
    """

    priority = priority.strip().capitalize()

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            "Priority must be High, Medium or Low."
        )

    return priority


def validate_status(status):
    """
    Validate task status.
    """

    status = status.strip().capitalize()

    if status not in VALID_STATUS:
        raise ValueError(
            "Status must be Pending or Completed."
        )

    return status


def validate_due_date(date_string):
    """
    Checks whether date is in YYYY-MM-DD format.
    """

    try:

        datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        return date_string

    except ValueError:

        raise ValueError(
            "Date must be in YYYY-MM-DD format."
        )


def validate_task_id(task_id):
    """
    Ensure task ID is positive.
    """

    if task_id <= 0:
        raise ValueError(
            "Task ID must be positive."
        )

    return task_id


def get_integer(message):
    """
    Keeps asking until a valid integer is entered.
    """

    while True:

        try:

            return int(input(message))

        except ValueError:

            print("Please enter a valid number.")


def confirm(message):
    """
    Returns True if user confirms.
    """

    while True:

        answer = input(
            f"{message} (Y/N): "
        ).strip().lower()

        if answer == "y":
            return True

        if answer == "n":
            return False

        print("Please enter Y or N.")


def print_heading(title):
    """
    Prints formatted headings.
    """

    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def pause():
    """
    Pause until Enter is pressed.
    """

    input("\nPress Enter to continue...")