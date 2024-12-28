from celery import shared_task
from django.core.mail import send_mail
from .models import ScheduledEmail

@shared_task
def send_scheduled_emails():
    """Отправляет все запланированные письма, время которых пришло."""
    emails = ScheduledEmail.objects.filter(is_sent=False, scheduled_time__lte=now())
    for email in emails:
        try:
            send_mail(
                subject=email.email_template.subject,
                message=email.email_template.body,
                from_email="sadykov-maskim-2003@yandex,ru",
                recipient_list=[email.to_email],
                fail_silently=False,
            )
            email.is_sent = True
            email.save()
        except Exception as e:
            # Логгирование ошибки
            print(f"Ошибка при отправке письма {email.id}: {e}")
