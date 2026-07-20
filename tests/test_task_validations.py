from utils import (
    validate_title,
    validate_description,
    validate_due_date,
    validate_priority,
)


def test_title_validation_trims_and_accepts_text():
    valid, value = validate_title("   Buy milk   ")
    assert valid is True
    assert value == "Buy milk"


def test_title_validation_rejects_empty_value():
    valid, message = validate_title("   ")
    assert valid is False
    assert "cannot be empty" in message.lower()


def test_description_validation_accepts_content():
    valid, value = validate_description("Pick up groceries")
    assert valid is True
    assert value == "Pick up groceries"


def test_due_date_validation_requires_yyyy_mm_dd_format():
    valid, value = validate_due_date("2026-07-17")
    assert valid is True
    assert value == "2026-07-17"

    valid, message = validate_due_date("07/17/2026")
    assert valid is False
    assert "yyyy-mm-dd" in message.lower()


def test_priority_validation_accepts_supported_values():
    valid, value = validate_priority("high")
    assert valid is True
    assert value == "High"

    valid, message = validate_priority("urgent")
    assert valid is False
    assert "high, medium, or low" in message.lower()


def test_add_task_normalizes_and_stores_strings(monkeypatch, tmp_path):
    import task_manager

    task_file = tmp_path / "tasks.json"
    monkeypatch.setattr(task_manager, "TASK_FILE", str(task_file))

    task = task_manager.add_task(
        user_id=1,
        title="   Buy milk   ",
        description="   Get bread   ",
        due_date="2026-07-17",
        priority="high",
    )

    assert task.title == "Buy milk"
    assert task.description == "Get bread"
    assert task.due_date == "2026-07-17"
    assert task.priority == "High"
