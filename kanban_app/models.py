from django.db import models
from django.contrib.auth.models import User

#Model für das Board
class Board(models.Model):
  owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name="owned_boards") #Wer hat es erstellt // related_name = direkter zugriff ohne _set
  members = models.ManyToManyField(User,related_name="boards",blank=True) #Wer darf es nutzen
  title = models.CharField(max_length=50)
  description = models.TextField( blank=True) #Beschreibung darf frei sein
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def __str__(self):
    return self.title


#Model für die Task
class Task(models.Model):
  board = models.ForeignKey(Board,related_name="tasks", on_delete=models.CASCADE)
  title = models.CharField(max_length=50)
  description = models.TextField(blank=True) #Beschreibung darf frei sein
  assignee =models.ForeignKey(User,related_name="assigned_tasks", on_delete= models.SET_NULL, null= True, blank=True)
  reviewers =models.ManyToManyField(User,related_name="review_tasks",blank=True)
  STATUS_CHOICE = [
     ("to-do", "to do"),
     ("in-progress", "in progress"),
     ("review","review")
    ]
  PRIORITY_CHOICE=[
     ("low", "low"),
     ("medium","medium"),
     ("high","high")
    ]
  status = models.CharField(max_length=15, choices= STATUS_CHOICE, default="to-do")
  priority = models.CharField(max_length=10, choices= PRIORITY_CHOICE, default="low")
  due_date = models.DateField(null=True, blank=True)
  comments_count = models.IntegerField(default=0)


  def __str__(self):
        return self.title
  

class Comment(models.Model):
   task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
   author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
   content = models.TextField() 
   created_at = models.DateTimeField(auto_now_add=True)


  
  