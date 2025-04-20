from django.db import models
from uuid import uuid4

# Create your models here.
class Task(models.Model):
    task_id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    email = models.EmailField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Task {self.task_id} for {self.email}"
    