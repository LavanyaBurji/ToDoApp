import hashlib


def generate_user_id(users):
    if not users:
        return 1

    return max(user["user_id"] for user in users) + 1


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password

def validate_username(username):
    if username == "":
        return False, "Username cannot be empty."

    return True, ""


def validate_email(email):
    if email == "":
        return False, "Email cannot be empty."

    if "@" not in email or "." not in email:
        return False, "Invalid email format."

    return True, ""


def validate_password(password):
    if password == "":
        return False, "Password cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    return True, ""