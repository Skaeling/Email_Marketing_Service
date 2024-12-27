import smtplib

from django.core.cache import cache
from django.core.mail import send_mail

from config.settings import DEFAULT_FROM_EMAIL
from sender.models import Message, Newsletter, Recipient


def mail_attempt(newsletter):
    to = list(newsletter.recipients.values_list('email', flat=True))
    if not to:
        return False, "Нет адресатов для рассылки"
    sender = DEFAULT_FROM_EMAIL
    title = newsletter.message.title
    message = newsletter.message.body
    try:
        response = send_mail(title, message, sender, to, fail_silently=False)
        print("Рассылка отправлена успешно")
        return True, response
    except smtplib.SMTPException as e:
        print(f"Ошибка при отправке письма: {e}")
        return False, str(e)


class UserDataCache:
    @classmethod
    def get_user_data(cls, user, data_type):
        key = f'{data_type}_{user}'
        data = cache.get(key)
        if data is None:
            if data_type == 'newsletters':
                data = Newsletter.objects.filter(owner=user)
            elif data_type == 'clients':
                data = Recipient.objects.filter(creator=user)
            elif data_type == 'messages':
                data = Message.objects.filter(author=user)
            else:
                return None
            cache.set(key, data, 60 * 5)
            if not data.exists():
                return None
        return data
