import json
import os
from config import USERS_FILE, TASKS_FILE

SESSION_FILE = "database/session.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def load_tasks():
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def load_session():
    try:
        with open(SESSION_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_session(session):
    with open(SESSION_FILE, "w") as file:
        json.dump(session, file, indent=4)


def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)