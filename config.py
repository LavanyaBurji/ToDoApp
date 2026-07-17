import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_DIR = os.path.join(BASE_DIR, "database")

USERS_FILE = os.path.join(DATABASE_DIR, "users.json")
TASKS_FILE = os.path.join(DATABASE_DIR, "tasks.json")