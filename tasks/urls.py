from django.urls import path
from .views import ProcessView, StatusView

urlpatterns = [
    path('process/', ProcessView.as_view(), name='process-task'),
    path('status/<str:task_id>/', StatusView.as_view(), name='task-status'),
]
