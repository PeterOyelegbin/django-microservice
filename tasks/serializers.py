from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['email', 'message', 'task_id', 'created_at']
        read_only_fields = ['task_id', 'created_at']
        