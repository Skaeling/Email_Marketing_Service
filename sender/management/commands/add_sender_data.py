from django.core.management.base import BaseCommand
from django.core.management import call_command
from sender.models import Recipient, Message, Newsletter, MailingAttempt


class Command(BaseCommand):
    help = 'Load test data from fixture'

    def handle(self, *args, **kwargs):
        MailingAttempt.objects.all().delete()
        Newsletter.objects.all().delete()
        Message.objects.all().delete()
        Recipient.objects.all().delete()

        call_command('loaddata', 'sender_fixture.json')
        self.stdout.write(self.style.SUCCESS('Successfully loaded data from fixture'))
