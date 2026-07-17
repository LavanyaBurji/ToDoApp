from dataclasses import dataclass, asdict


@dataclass
class Task:
    """
    Represents a single task.
    """

    task_id: int
    user_id: int
    title: str
    description: str
    due_date: str
    priority: str
    status: str = "Pending"

    def to_dict(self):
        """
        Convert Task object into dictionary
        so it can be stored as JSON.
        """
        return asdict(self)

    @staticmethod
    def from_dict(data):
        """
        Convert dictionary into Task object.
        """

        return Task(
            task_id=data["task_id"],
            user_id=data["user_id"],
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"],
            priority=data["priority"],
            status=data.get("status", "Pending")
        )

    def mark_completed(self):
        """
        Mark task as completed.
        """
        self.status = "Completed"

    def update(
        self,
        title,
        description,
        due_date,
        priority
    ):
        """
        Update task details.
        """

        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority