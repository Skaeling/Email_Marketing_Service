from django.db import models
from django.urls import reverse

from users.models import CustomUser


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    fullname = models.CharField(max_length=100, verbose_name='ФИО')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')
    creator = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='recipients',
                                verbose_name="Кем добавлен")

    def get_absolute_url(self):
        return reverse("sender:recipient_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.fullname} ({self.email})'

    class Meta:
        verbose_name = 'получатель'
        verbose_name_plural = 'получатели'
        ordering = ["email", ]
        permissions = [
            ('can_view_all_clients', 'Can view all clients'),

        ]


class Message(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    body = models.TextField(verbose_name='Сообщение')
    author = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='messages',
                               verbose_name="Автор")

    def get_absolute_url(self):
        return reverse("sender:message_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.title}: {self.body[:100]}'

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        ordering = ["title", ]
        permissions = [
            ('can_view_all_messages', 'Can view all messages'),

        ]


class Newsletter(models.Model):
    CREATED = 'created'
    STARTED = 'started'
    CLOSED = 'closed'

    NEWSLETTER_STATUS_CHOISES = [
        (CREATED, 'Создана'),
        (STARTED, 'Запущена'),
        (CLOSED, 'Завершена'),
    ]
    first_sent = models.DateTimeField(null=True, blank=True, verbose_name='Дата старта')
    last_sent = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    status = models.CharField(max_length=7, choices=NEWSLETTER_STATUS_CHOISES, default=CREATED, verbose_name='Статус')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='newsletters')
    recipients = models.ManyToManyField(Recipient, related_name='newsletter_received')
    owner = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name='newsletters', verbose_name="Владелец")

    def __str__(self):
        return f'Рассылка №{self.pk}'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        ordering = ["first_sent", ]
        permissions = [
            ('can_view_all_newsletters', 'Can view all newsletters'),
            ('can_change_newsletter_status', 'Can change newsletter status'),

        ]


class MailingAttempt(models.Model):
    SUCCESSFUL = 'success'
    UNSUCCESSFUL = 'error'
    ATTEMPT_STATUS_CHOICES = [
        (SUCCESSFUL, 'Успешно'),
        (UNSUCCESSFUL, 'Не успешно')
    ]
    attempt_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    exc_state = models.CharField(max_length=15, choices=ATTEMPT_STATUS_CHOICES, default=UNSUCCESSFUL,
                                 verbose_name='Статус отправки')
    server_response = models.TextField(blank=True, null=True, default="")
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='mailing_attempts')

    def __str__(self):
        return f'{self.attempt_date} осуществлена попытка отправки {self.newsletter} ' \
               f'с результатом: "{self.exc_state}" Лог операции: "{self.server_response}"'

    class Meta:
        verbose_name = 'попытка'
        verbose_name_plural = 'попытки'
        ordering = ["-id", ]
