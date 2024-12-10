import os

from django.shortcuts import render
from django.utils import timezone
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Recipient, Message, Newsletter, MailingAttempt
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from .forms import RecipientForm, MessageForm, NewsletterForm


def home(request):
    clients = Recipient.objects.order_by('email').distinct('email')
    all_mailings = Newsletter.objects.count()
    active_mailings = Newsletter.objects.filter(status=Newsletter.STARTED)
    result = active_mailings.count()
    extra_context = {'title': 'Send-or-Treat',
                     'email': clients,
                     'active_mail': result,
                     'all_mailings': all_mailings

                     }
    return render(request, 'sender/home.html', extra_context)


# CLIENT
class RecipientListView(ListView):
    model = Recipient
    template_name = 'sender/recipients_list.html'
    context_object_name = 'recipient'
    extra_context = {'title': 'Список получателей'}


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать получателя'}


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать получателя'}

    # def get_success_url(self, **kwargs):
    #     return reverse("blog:post_detail", kwargs={'pk': self.object.pk})


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'sender/recipient_detail.html'
    context_object_name = 'client'
    extra_context = {'title': 'Детальная информация о получателе'}


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'sender/confirm_delete_form.html'
    extra_context = {'title': 'Удаление получателя'}
    success_url = reverse_lazy('sender:recipients_list')


# MESSAGE
class MessageListView(ListView):
    model = Message
    template_name = 'sender/messages_list.html'
    context_object_name = 'messages'
    extra_context = {'title': 'Список сообщений'}


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать сообщение'}


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать сообщение'}

    # def get_success_url(self, **kwargs):
    #     return reverse("blog:post_detail", kwargs={'pk': self.object.pk})


class MessageDetailView(DetailView):
    model = Message
    template_name = 'sender/message_detail.html'
    context_object_name = 'message'
    extra_context = {'title': 'Детальная информация о сообщении'}


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'sender/confirm_delete_form.html'
    extra_context = {'title': 'Удаление сообщения'}
    success_url = reverse_lazy('sender:messages_list')


#  NEWSLETTER

class NewsletterListView(ListView):
    model = Newsletter
    template_name = 'sender/newsletters_list.html'
    context_object_name = 'newsletters'
    extra_context = {'title': 'Список доступных рассылок'}


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать рассылку'}

    def get_success_url(self, **kwargs):
        return reverse("sender:newsletter_detail", kwargs={'pk': self.object.pk})


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать рассылку'}

    def get_success_url(self, **kwargs):
        return reverse("sender:newsletter_detail", kwargs={'pk': self.object.pk})


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = 'sender/newsletter_detail.html'
    context_object_name = 'newsletter'
    extra_context = {'title': 'Детальная информация о рассылке'}


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = 'sender/confirm_delete_form.html'
    extra_context = {'title': 'Удаление рассылки'}
    success_url = reverse_lazy('sender:newsletters_list')


# class MailingAttemptCreateView(CreateView):
#     model = MailingAttempt
#     fields = ['attempt_date', 'exc_state', 'server_response', 'newsletter']
#     template_name = 'sender/send_newsletter.html'
#     context_object_name = 'newsletter'
#     extra_context = {'title': 'Отправить рассылку'}

# def get_success_url(self, **kwargs):
#     return reverse("sender:newsletter_detail", kwargs={'pk': self.object.pk})


def mail_send(request, pk):
    mailing = Newsletter.objects.get(pk=pk)
    email_list = list(mailing.recipients.values_list('email', flat=True))
    sender = os.getenv('EMAIL_DEFAULT_USER')

    # выключатель рассылки
    to = []

    title = mailing.message.title
    message = mailing.message.body
    if send_mail(title, message, sender, to, fail_silently=False):
        attempt = MailingAttempt.objects.create(attempt_date=timezone.now(), exc_state=MailingAttempt.SUCCESSFUL,
                                                newsletter_id=pk)
        attempt.save()
        if mailing.status == 'created':
            mailing.status = 'started'
            mailing.first_sent = timezone.now()
            mailing.save()
        context = {
            'title': 'Успешно',
            'header': 'Рассылка отправлена'
        }
        return render(request, 'sender/send_newsletter.html', context)
    else:
        attempt = MailingAttempt.objects.create(attempt_date=timezone.now(), server_response='error', newsletter_id=pk)
        attempt.save()
        print("error")
        context = {
            'title': 'Ошибка!',
            'header': 'Ознакомьтесь с логом ошибки'
        }
        return render(request, 'sender/send_newsletter.html', context)
