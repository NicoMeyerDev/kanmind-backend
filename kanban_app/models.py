from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    """
    Represents a project board that groups tasks.
    Each board has an owner and can have multiple members.
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards"
    )

    members = models.ManyToManyField(
        User,
        related_name="boards",
        blank=True
    )

    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return the board title for display in admin and shell.
        """
        return self.title


class Task(models.Model):
    """
    Represents a task within a board.
    A task can be assigned to one user and reviewed by multiple users.
    """

    board = models.ForeignKey(
        Board,
        related_name="tasks",
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    assignee = models.ForeignKey(
        User,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    reviewers = models.ManyToManyField(
        User,
        related_name="done_tasks",
        blank=True
    )

    STATUS_CHOICE = [
        ("to-do", "to do"),
        ("in-progress", "in progress"),
        ("review", "review"),
        ("done", "done"),
    ]

    PRIORITY_CHOICE = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ]

    status = models.CharField(max_length=15, choices=STATUS_CHOICE, default="to-do")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICE, default="low")
    due_date = models.DateField(null=True, blank=True)

    comments_count = models.IntegerField(default=0)

    def __str__(self):
        """
        Return the task title for display.
        """
        return self.title


class Comment(models.Model):
    """
    Represents a comment on a task.
    Each comment is linked to a single task and author.
    """

    task = models.ForeignKey(
        Task,
        related_name="comments",
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)