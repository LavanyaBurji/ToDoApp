import hashlib
from datetime import datetime


def generate_user_id(users):
    if not users:
        return 1

    return max(user["user_id"] for user in users) + 1


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password


def validate_username(username):
    username = username.strip()
    if username == "":
        return False, "Username cannot be empty."

    return True, ""


def validate_email(email):
    email = email.strip()
    if email == "":
        return False, "Email cannot be empty."

    if "@" not in email or "." not in email:
        return False, "Invalid email format."

    return True, ""


def validate_password(password):
    if password == "":
        return False, "Password cannot be empty."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."

    return True, ""


def validate_title(title):
    title = title.strip()
    if title == "":
        return False, "Title cannot be empty."

    return True, title


def validate_description(description):
    description = description.strip()
    if description == "":
        return False, "Description cannot be empty."

    return True, description


def validate_due_date(due_date):
    due_date = due_date.strip()
    if due_date == "":
        return False, "Due date cannot be empty."

    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        return False, "Due date must be in YYYY-MM-DD format."

    return True, due_date


def validate_priority(priority):
    priority = priority.strip().capitalize()
    if priority not in {"High", "Medium", "Low"}:
        return False, "Priority must be High, Medium, or Low."

    return True, priority