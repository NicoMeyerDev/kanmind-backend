from django.db import models
from django.contrib.auth.models import User


#Board-Modell:
#Ein Board hat einen Owner, mehrere Mitglieder und enthält später Tasks.
class Board(models.Model):
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

    #String-Darstellung im Admin / in der Shell
    def __str__(self):
        return self.title


#Task-Modell:
#Eine Task gehört zu genau einem Board und kann einem Bearbeiter sowie optional einem oder mehreren Reviewern zugeordnet werden.

class Task(models.Model):
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

    #Erlaubte Statuswerte für Tasks
    STATUS_CHOICE = [
        ("to-do", "to do"),
        ("in-progress", "in progress"),
        ("review", "review"),
        ("done", "done"),
    ]

    #Erlaubte Prioritätswerte für Tasks
    PRIORITY_CHOICE = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ]

    status = models.CharField(max_length=15, choices=STATUS_CHOICE, default="to-do")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICE, default="low")
    due_date = models.DateField(null=True, blank=True)

    #Wird für die API-Antworten genutzt
    comments_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


#Comment-Modell:
#Ein Kommentar gehört zu genau einer Task und hat genau einen Autor.
class Comment(models.Model):
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
  
  