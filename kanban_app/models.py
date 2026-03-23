from django.db import models
from django.contrib.auth.models import User

#Model für das Board
class Board(models.Model):
  owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name="owned_boards") #Wer hat es erstellt
  members = models.ManyToManyField(User,related_name="boards",blank=True) #Wer darf es nutzen
  title = models.CharField(max_length=50)
  description = models.TextField(max_length=250, blank=True) #Beschreibung max. 250 lang, darf frei sein
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.title


#Model für die Task
class Task(models.Model):
  board = models.ForeignKey(Board, on_delete=models.CASCADE)
  title = models.CharField(max_length=50)
  description = models.TextField(max_length=250, blank=True) #Beschreibung max. 250 lang, darf frei sein
  STATUS_CHOICE = [
     ("nicht_begonnen", "Nicht begonnen"),
     ("begonnen", "Begonnen"),
     ("erledigt","Erledigt")
    ]
  PRIORITY_CHOICE=[
     ("niedrig", "Niedrig"),
     ("mittel","Mittel"),
     ("hoch","Hoch")
    ]
  status = models.CharField(max_length=15, choices= STATUS_CHOICE, default="nicht_begonnen")
  priority = models.CharField(max_length=10, choices= PRIORITY_CHOICE, default="niedrig")


  def __str__(self):
        return self.title
  