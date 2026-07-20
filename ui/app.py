import sys
from datetime import datetime
from flask import Flask, redirect, render_template, request, session, url_for, flash
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from auth import login_user, logout, register_user
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
    get_statistics,
    get_task_summary,
    get_overdue_tasks,
)

app = Flask(__name__)
app.secret_key = "change-this-secret"


def sort_tasks(tasks, sort_key):
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    if sort_key == "due_date":
        return sorted(tasks, key=lambda task: datetime.strptime(task.due_date, "%Y-%m-%d"))
    if sort_key == "priority":
        return sorted(tasks, key=lambda task: priority_order.get(task.priority, 4))
    return tasks


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login_view"))

    user = session["user"]
    tasks = get_all_tasks(user["user_id"])
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    sort = request.args.get("sort", "").strip()

    active_filters = []

    if search:
        tasks = [
            task
            for task in tasks
            if search.lower() in task.title.lower() or search.lower() in task.description.lower()
        ]
        active_filters.append(f"Search: {search}")

    if status:
        normalized_status = status.capitalize()
        tasks = [task for task in tasks if task.status == normalized_status]
        active_filters.append(normalized_status)

    if priority:
        normalized_priority = priority.capitalize()
        tasks = [task for task in tasks if task.priority == normalized_priority]
        active_filters.append(normalized_priority)

    if sort:
        tasks = sort_tasks(tasks, sort)
        active_filters.append(f"Sorted by {sort.replace('_', ' ')}")

    stats = get_statistics(user["user_id"])
    summary = get_task_summary(user["user_id"])
    overdue = get_overdue_tasks(user["user_id"])
    return render_template(
        "index.html",
        user=user,
        stats=stats,
        summary=summary,
        overdue=overdue,
        tasks=tasks,
        now_date=str(datetime.today().date()),
        search=search,
        status=status,
        priority=priority,
        sort=sort,
        active_filters=active_filters,
    )


@app.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = login_user(username, password)
        if user:
            session["user"] = user
            save_session(user)
            return redirect(url_for("index"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_view():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        try:
            register_user(username, email, password)
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login_view"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("register.html")


@app.route("/logout")
def logout_view():
    session.pop("user", None)
    clear_session()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login_view"))


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task_view():
    if "user" not in session:
        return redirect(url_for("login_view"))

    user = session["user"]

    form_data = {
        "title": "",
        "description": "",
        "due_date": "",
        "priority": "Medium",
    }

    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", "").strip(),
            "due_date": request.form.get("due_date", "").strip(),
            "priority": request.form.get("priority", "").strip() or "Medium",
        }

        try:
            add_task(
                user["user_id"],
                form_data["title"],
                form_data["description"],
                form_data["due_date"],
                form_data["priority"],
            )
            flash("Task added successfully.", "success")
            return redirect(url_for("index"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("task_form.html", action="Add Task", task=form_data)
@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task_view(task_id):
    if "user" not in session:
        return redirect(url_for("login_view"))

    user = session["user"]
    task = get_task_by_id(user["user_id"], task_id)
    if not task:
        flash("Task not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", "").strip(),
            "due_date": request.form.get("due_date", "").strip(),
            "priority": request.form.get("priority", "").strip() or "Medium",
        }

        if update_task(
            user["user_id"],
            task_id,
            form_data["title"],
            form_data["description"],
            form_data["due_date"],
            form_data["priority"],
        ):
            flash("Task updated successfully.", "success")
            return redirect(url_for("index"))

        flash("Unable to update task. Please check your values.", "danger")
        task = form_data

    return render_template("task_form.html", action="Edit Task", task=task)


@app.route("/tasks/delete/<int:task_id>")
def delete_task_view(task_id):
    if "user" not in session:
        return redirect(url_for("login_view"))

    user = session["user"]
    if delete_task(user["user_id"], task_id):
        flash("Task deleted.", "success")
    else:
        flash("Task not found.", "danger")

    return redirect(url_for("index"))


@app.route("/tasks/complete/<int:task_id>")
def complete_task_view(task_id):
    if "user" not in session:
        return redirect(url_for("login_view"))

    user = session["user"]
    if mark_completed(user["user_id"], task_id):
        flash("Task marked complete.", "success")
    else:
        flash("Task not found.", "danger")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
