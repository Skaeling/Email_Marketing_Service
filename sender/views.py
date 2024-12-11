import os

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Recipient, Message, Newsletter, MailingAttempt
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from .forms import RecipientForm, MessageForm, NewsletterForm, MailingAttemptForm
from django.contrib.auth.mixins import LoginRequiredMixin


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


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать получателя'}

    def form_valid(self, form):
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.creator = self.request.user
            recipient.save()

        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
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


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
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

    def form_valid(self, form):
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.owner = self.request.user
            newsletter.save()

        return super().form_valid(form)


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


class NewsletterDeleteView(LoginRequiredMixin, DeleteView):
    model = Newsletter
    template_name = 'sender/confirm_delete_form.html'
    extra_context = {'title': 'Удаление рассылки'}
    success_url = reverse_lazy('sender:newsletters_list')


class MailingAttemptCreateView(CreateView, ListView):
    model = Newsletter
    form_class = MailingAttemptForm
    context_object_name = 'newsletters'
    template_name = 'sender/mailing_create.html'
    extra_context = {'title': 'Мои рассылки',
                     'header': 'Выберите из списка'
                     }
    success_url = reverse_lazy('sender:send_newsletter')

    def get_success_url(self, **kwargs):
        return reverse("sender:send_newsletter")

    # def get_form_class(self):
    #     newsletter = self.get_object(queryset=None)
    #     if newsletter.owner == self.request.user:
    #         return MailingAttemptForm
    #     raise PermissionDenied

    def form_valid(self, form):
        if form.is_valid():
            attempt = form.save(commit=False)
            newsletter = Newsletter.objects.get(pk=attempt.newsletter.pk)
            if mail_attempt(newsletter.pk):
                attempt.exc_state = MailingAttempt.SUCCESSFUL
                if newsletter.status == 'created':
                    newsletter.status = 'started'
                    newsletter.first_sent = timezone.now()
                    newsletter.save()
                attempt.save()
                self.extra_context = {
                    'title': 'Успешно',
                    'header': 'Рассылка отправлена'
                }
                print(f'Попытка рассылки состоялась')
            else:
                attempt.server_response = 'error'
                attempt.save()
                print("error")
                self.extra_context = {
                    'title': 'Ошибка!',
                    'header': 'Ознакомьтесь с логом ошибки'
                }
        return redirect(self.success_url)




def mail_attempt(pk):
    newsletter = Newsletter.objects.get(pk=pk)
    email_list = list(newsletter.recipients.values_list('email', flat=True))
    sender = os.getenv('EMAIL_DEFAULT_USER')

    to = []  # заменить значение на email_list для включения опции рассылки

    title = newsletter.message.title
    message = newsletter.message.body
    return send_mail(title, message, sender, to, fail_silently=False)


class MailingAttemptListView(MailingAttemptCreateView, ListView):
    model = MailingAttempt
    template_name = 'sender/send_newsletter.html'
    context_object_name = 'mailings'



## old version
# def mail_send(request, pk):
#     mailing = Newsletter.objects.get(pk=pk)
#     email_list = list(mailing.recipients.values_list('email', flat=True))
#     sender = os.getenv('EMAIL_DEFAULT_USER')
#
#     # выключатель рассылки
#     to = []
#
#     title = mailing.message.title
#     message = mailing.message.body
#     if send_mail(title, message, sender, to, fail_silently=False):
#         attempt = MailingAttempt.objects.create(exc_state=MailingAttempt.SUCCESSFUL, newsletter_id=pk)
#         attempt.save()
#         if mailing.status == 'created':
#             mailing.status = 'started'
#             mailing.first_sent = timezone.now()
#             mailing.save()
#         context = {
#             'title': 'Успешно',
#             'header': 'Рассылка отправлена'
#         }
#         return render(request, 'sender/send_newsletter.html', context)
#     else:
#         attempt = MailingAttempt.objects.create(server_response='error', newsletter_id=pk)
#         attempt.save()
#         print("error")
#         context = {
#             'title': 'Ошибка!',
#             'header': 'Ознакомьтесь с логом ошибки'
#         }
#         return render(request, 'sender/send_newsletter.html', context)
