from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import time, logging

logger = logging.getLogger(__name__)
    
@shared_task(bind=True, max_retries=3)
def process_task(self, email, message):
    try:
        time.sleep(10)
        send_mail(
            subject='Django Microservice Notification',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        result = f'Successfully sent email to {email}'
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    