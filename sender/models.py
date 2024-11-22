from django.db import models
from django.urls import reverse


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    fullname = models.CharField(max_length=100, verbose_name='ФИО')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    def get_absolute_url(self):
        return reverse("sender:recipient_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.fullname} ({self.email})'

    class Meta:
        verbose_name = 'получатель'
        verbose_name_plural = 'получатели'
        ordering = ["email", ]


class Message(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    body = models.TextField(verbose_name='Сообщение')

    def get_absolute_url(self):
        return reverse("sender:message_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.title}: {self.body[:100]}'

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        ordering = ["title", ]


class Newsletter(models.Model):
    CREATED = 'created'
    STARTED = 'started'
    CLOSED = 'closed'

    NEWSLETTER_STATUS_CHOISES = [
        (CREATED, 'Создана'),
        (STARTED, 'Запущена'),
        (CLOSED, 'Завершена'),
    ]
    first_sent = models.DateTimeField(auto_now=True, verbose_name='Дата старта')
    last_sent = models.DateTimeField(auto_now=True, verbose_name='Дата завершения')
    status = models.CharField(max_length=7, choices=NEWSLETTER_STATUS_CHOISES, default=CREATED, verbose_name='Статус')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='newsletters')
    recipients = models.ManyToManyField(Recipient, related_name='newsletter_received')

    def __str__(self):
        return f'Отправлена:{self.first_sent} Статус:{self.status} ' \
               f'Сообщение:{self.message} Получатели:({self.recipients})'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        ordering = ["first_sent", ]


class MailingAttempt(models.Model):
    SUCCESSFUL = 'success'
    UNSUCCESSFUL = 'error'
    ATTEMPT_STATUS_CHOICES = [
        (SUCCESSFUL, 'Успешно'),
        (UNSUCCESSFUL, 'Не успешно')
    ]
    attempt_date = models.DateTimeField(verbose_name="Дата и время попытки")
    exc_state = models.CharField(max_length=15, choices=ATTEMPT_STATUS_CHOICES, default=UNSUCCESSFUL, verbose_name='Статус отправки')
    server_response = models.TextField(blank=True, null=True, default="")
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='mailing_attempts')

    def __str__(self):
        return f'{self.attempt_date} осуществлена попытка отправки рассылки {self.newsletter} ' \
               f'с результатом:{self.exc_state} Лог операции:{self.server_response}'

    class Meta:
        verbose_name = 'попытка'
        verbose_name_plural = 'попытки'
        ordering = ["exc_state", ]
