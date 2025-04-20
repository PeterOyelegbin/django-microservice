from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Task
from unittest.mock import patch

# Create your tests here.
class TaskProcessingIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.process_url = reverse('process-task')
        self.valid_payload = {
            'email': 'test@example.com',
            'message': 'Test message'
        }
        self.invalid_payload = {
            'email': 'not-an-email',
            'message': ''
        }

    @patch('tasks.views.process_task.apply_async')
    def test_process_task_success(self, mock_apply_async):
        """Test successful task processing"""
        response = self.client.post(self.process_url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        self.assertIn('check_status_url', response.data)
        # Verify task was created in database
        task_id = response.data['task_id']
        task = Task.objects.get(task_id=task_id)
        self.assertEqual(task.email, self.valid_payload['email'])
        self.assertEqual(task.message, self.valid_payload['message'])

    def test_process_task_invalid_data(self):
        """Test with invalid payload"""
        response = self.client.post(self.process_url, data=self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('tasks.views.process_task.AsyncResult')
    def test_check_task_status_success(self, mock_async_result):
        """Test checking task status"""
        # Create a test task
        task = Task.objects.create(email='status@test.com', message='Status check')
        # Mock Celery result
        mock_result = mock_async_result.return_value
        mock_result.status = 'SUCCESS'
        mock_result.ready.return_value = True
        mock_result.result = 'Processed successfully'
        status_url = reverse('task-status', kwargs={'task_id': str(task.task_id)})  # Update URL name
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_id'], str(task.task_id))
        self.assertEqual(response.data['status'], 'SUCCESS')
        self.assertEqual(response.data['result'], 'Processed successfully')
        mock_async_result.assert_called_once_with(str(task.task_id))

    def test_check_nonexistent_task_status(self):
        """Test checking status for non-existent task"""
        non_existent_id = '00000000-0000-0000-0000-000000000000'
        status_url = reverse('task-status', kwargs={'task_id': non_existent_id})
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Task not found')

    @patch('tasks.views.process_task.apply_async', side_effect=Exception('Test error'))
    def test_process_task_server_error(self, mock_apply_async):
        """Test server error during task processing"""
        response = self.client.post(self.process_url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'Internal server error')
        self.assertEqual(response.data['details'], 'Test error')

    @patch('tasks.views.process_task.AsyncResult', side_effect=Exception('Status error'))
    def test_check_task_status_server_error(self, mock_async_result):
        """Test server error when checking task status"""
        task = Task.objects.create(email='error@test.com', message='Error check')
        status_url = reverse('task-status', kwargs={'task_id': str(task.task_id)})
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'Internal server error')
        self.assertEqual(response.data['details'], 'Status error')
