import os

from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Recipient, Message, Newsletter, MailingAttempt
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from .forms import RecipientForm, MessageForm, NewsletterForm, MailingAttemptForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


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
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'sender/recipients_list.html'
    context_object_name = 'recipients'
    extra_context = {'title': 'Список получателей'}

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.has_perm('sender.can_view_recipients'):
            return queryset
        return queryset.filter(creator=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать получателя'}
    # permission_required = 'sender.add_recipient'
    # permission_denied_message = 'Недостаточно прав для действия'

    def form_valid(self, form):
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.creator = self.request.user
            recipient.save()

        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать получателя'}
    permission_required = 'sender.change_recipient'


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

    def get_object(self, queryset=None):
        recipient = super().get_object(queryset)
        user = self.request.user
        if not user.has_perm('sender.can_delete_recipient') or user != recipient.creator:
            raise PermissionDenied
        return recipient


# MESSAGE
class MessageListView(ListView):
    model = Message
    template_name = 'sender/messages_list.html'
    context_object_name = 'messages'
    extra_context = {'title': 'Список сообщений'}


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать сообщение'}


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать сообщение'}


class MessageDetailView(DetailView):
    model = Message
    template_name = 'sender/message_detail.html'
    context_object_name = 'message'
    extra_context = {'title': 'Детальная информация о сообщении'}


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'sender/confirm_delete_form.html'
    extra_context = {'title': 'Удаление сообщения'}
    success_url = reverse_lazy('sender:messages_list')


#  NEWSLETTER

class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = 'sender/newsletters_list.html'
    context_object_name = 'newsletters'
    extra_context = {'title': 'Список доступных рассылок'}


class NewsletterCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать рассылку'}
    permission_required = 'sender.add_newsletter'

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


class MailingAttemptCreateView(SuccessMessageMixin, CreateView, ListView):
    model = Newsletter
    form_class = MailingAttemptForm
    context_object_name = 'newsletters'
    template_name = 'sender/mailing_create.html'
    success_url = reverse_lazy("sender:send_newsletter")
    extra_context = {'title': 'Мои рассылки',
                     'header': 'Выберите из списка'
                     }

    def get_success_url(self, **kwargs):
        return reverse_lazy("sender:mailing_attempts")

    # def get_form_class(self):
    #     newsletter = self.get_object(queryset=None)
    #     if newsletter.owner == self.request.user:
    #         return MailingAttemptForm
    #     raise PermissionDenied

    def form_valid(self, form):
        if form.is_valid():
            attempt = form.save(commit=False)
            newsletter = Newsletter.objects.get(pk=attempt.newsletter.pk)
            if mail_attempt(newsletter):
                attempt.exc_state = MailingAttempt.SUCCESSFUL
                if newsletter.status == 'created':
                    newsletter.status = 'started'
                    newsletter.first_sent = timezone.now()
                    newsletter.save()
                attempt.save()

                success_message = "Рассылка успешно отправлена"
                print(f'Попытка рассылки состоялась')
            else:
                attempt.server_response = 'error'
                attempt.save()
                print("error")
                success_message = "Ошибка при отправке рассылки"
        return HttpResponseRedirect(reverse('sender:mailing_attempts') + f'?success_message={success_message}')


def mail_attempt(newsletter):
    email_list = list(newsletter.recipients.values_list('email', flat=True))
    sender = os.getenv('EMAIL_DEFAULT_USER')
    to = []  # заменить [] на email_list для включения опции рассылки

    title = newsletter.message.title
    message = newsletter.message.body
    return send_mail(title, message, sender, to, fail_silently=False)


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = 'sender/mailing_attempts.html'
    context_object_name = 'mailings'
    extra_context = {'title': 'Мои рассылки',
                     'header': 'Результаты отправки'
                     }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        success_message = self.request.GET.get('success_message')
        if success_message:
            context['success_message'] = success_message
        return context
