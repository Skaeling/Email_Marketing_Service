import smtplib

from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from django.utils import timezone

from config.settings import DEFAULT_FROM_EMAIL

from sender.models import Newsletter, MailingAttempt


class Command(BaseCommand):
    help = 'Send newsletter'

    def handle(self, *args, **kwargs):
        def send_letter():
            self.stdout.write('Старт отправки')
            current_datetime = timezone.now()
            for newsletter in Newsletter.objects.filter(status__in=('started', 'created')):
                if not (newsletter.first_sent and newsletter.last_sent):
                    print(f'{newsletter} не отправлена. Не установлены даты отправки.'
                          f'Вы можете изменить параметры рассылки или выполнить отправку вручную')
                    continue

                if not (newsletter.first_sent < current_datetime < newsletter.last_sent):
                    continue

                if not newsletter.recipients.exists():
                    self.stdout.write(f'Нет получателей у рассылки №{newsletter.id}')
                    continue
                try:
                    emails = list(newsletter.recipients.values_list('email', flat=True))
                    response = send_mail(
                        subject=newsletter.message.title,
                        message=newsletter.message.body,
                        from_email=DEFAULT_FROM_EMAIL,
                        recipient_list=emails,
                        fail_silently=False
                    )
                    attempt = MailingAttempt.objects.create(
                        attempt_date=current_datetime,
                        exc_state=MailingAttempt.SUCCESSFUL,
                        server_response=response, newsletter=newsletter)

                    if newsletter.status == 'created':
                        newsletter.status = 'started'
                        newsletter.first_sent = current_datetime
                        newsletter.save()
                    print(attempt)
                except smtplib.SMTPException as e:
                    error = MailingAttempt.objects.create(
                        attempt_date=current_datetime, server_response=e,
                        newsletter=newsletter)
                    print(error)
            self.stdout.write('Конец отправки')
        send_letter()
