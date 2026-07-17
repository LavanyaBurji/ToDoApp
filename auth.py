from storage import load_users, save_users
from utils import (
    generate_user_id,
    hash_password,
    verify_password,
    validate_username,
    validate_email,
    validate_password
)

def register():
    users = load_users()

    while True:
        username = input("Enter username: ").strip()

        valid, message = validate_username(username)

        if valid:
            break

        print(message)

    for user in users:
        if user["username"].lower() == username.lower():
            print("Username already exists.")
            return

    while True:
        email = input("Enter email: ").strip()

        valid, message = validate_email(email)

        if valid:
            break

        print(message)

    for user in users:
        if user["email"].lower() == email.lower():
            print("Email already registered.")
            return

    while True:
        password = input("Enter password: ").strip()

        valid, message = validate_password(password)

        if valid:
            break

        print(message)

    new_user = {
        "user_id": generate_user_id(users),
        "username": username,
        "email": email,
        "password": hash_password(password)
    }

    users.append(new_user)
    save_users(users)

    print("Registration successful.")


def login():
    users = load_users()

    username = input("Enter username: ").strip()

    if username == "":
        print("Username cannot be empty.")
        return None

    password = input("Enter password: ").strip()

    if password == "":
        print("Password cannot be empty.")
        return None

    for user in users:
        if user["username"].lower() == username.lower():

            if verify_password(password, user["password"]):
                print(f"Login successful. Welcome, {user['username']}!")
                return user

            print("Incorrect password.")
            return None

    print("User not found.")
    return None


def logout():
    print("You have been logged out successfully.")
    return None