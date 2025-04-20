from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from .models import Task
from .serializers import TaskSerializer
from .tasks import process_task

# Create your views here.
class ProcessView(APIView):
    @swagger_auto_schema(request_body=TaskSerializer, responses={202: 'ACCEPTED', 400: 'BAD REQUEST', 500: 'SERVER ERROR'})
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            task = Task.objects.create(email=serializer.validated_data['email'], message=serializer.validated_data['message'])
            process_task.apply_async(args=[task.email, task.message], task_id=str(task.task_id))
            return Response({
                'status': 'Success',
                'task_id': task.task_id,
                'check_status_url': f'/api/status/{task.task_id}/'
            }, status=status.HTTP_202_ACCEPTED)
        except ValidationError as e:
            return Response({'status': 'Fail', 'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'Fail', 'error': 'Internal server error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class StatusView(APIView):
    @swagger_auto_schema(responses={200: 'OK', 404: 'NOT FOUND', 500: 'SERVER ERROR'})
    def get(self, request, task_id):
        try:
            task = Task.objects.get(task_id=task_id)
            celery_result = process_task.AsyncResult(task_id)
            response_data = {
                'task_id': task_id,
                'email': task.email,
                'message': task.message,
                'status': celery_result.status,
                'result': celery_result.result if celery_result.ready() else None,
                'created_at': task.created_at
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'status': 'Fail', 'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'Fail', 'error': 'Internal server error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        