
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView

from .models import Recipient, Message, Newsletter, MailingAttempt
from django.urls import reverse_lazy, reverse
from .forms import RecipientForm, MessageForm, NewsletterForm, MailingAttemptForm, ModeratorNewsletterForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import mail_attempt, UserDataCache


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
    template_name = 'sender/recipients.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.has_perm('sender.can_view_all_clients'):
            return queryset
        return queryset.filter(creator=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список получателей'
        context['headers'] = ['Электронная почта', 'ФИО', 'ID', 'Опции']

        return context


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


class RecipientUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать получателя'}
    success_message = "Обновления сохранены"

    def get_object(self, queryset=None):
        recipient = super().get_object(queryset)
        user = self.request.user
        if user.is_staff or user == recipient.creator:
            return recipient
        raise PermissionDenied


@method_decorator(cache_page(60 * 5), name='dispatch')
class RecipientDetailView(LoginRequiredMixin, DetailView):
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
        if user.is_staff or user == recipient.creator:
            return recipient
        raise PermissionDenied


                                                                # MESSAGE

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'sender/messages.html'
    context_object_name = 'messages_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.has_perm('sender.can_view_all_messages'):
            return queryset
        return queryset.filter(author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список сообщений'
        context['headers'] = ['Заголовок', 'Тело сообщения', 'ID', 'Опции']

        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать сообщение'}

    def form_valid(self, form):
        if form.is_valid():
            message = form.save(commit=False)
            message.author = self.request.user
            message.save()

        return super().form_valid(form)


class MessageUpdateView(SuccessMessageMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать сообщение'}
    success_message = "Обновления сохранены"

    def get_object(self, queryset=None):
        message = super().get_object(queryset)
        user = self.request.user
        if user.is_staff or user == message.author:
            return message
        raise PermissionDenied


@method_decorator(cache_page(60 * 15), name='dispatch')
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

    def get_object(self, queryset=None):
        message = super().get_object(queryset)
        user = self.request.user
        if user.is_staff or user == message.author:
            return message
        raise PermissionDenied


                                                            #  NEWSLETTER


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = 'sender/newsletters.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.has_perm('sender.can_view_all_newsletters'):
            return queryset
        return queryset.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список доступных рассылок'
        context['headers'] = ['ID', 'Дата старта', 'Дата завершения', 'Текущий статус', 'Сообщение',
                              'Получатели', 'Опции']
        context['clients'] = UserDataCache.get_user_data(self.request.user, 'clients')
        context['user_messages'] = UserDataCache.get_user_data(self.request.user, 'messages')
        return context


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Создать рассылку'}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse("sender:newsletter_detail", kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.owner = self.request.user
            newsletter.save()

        return super().form_valid(form)


class NewsletterUpdateView(SuccessMessageMixin, UpdateView):
    model = Newsletter
    template_name = 'sender/create_form.html'
    extra_context = {'title': 'Редактировать рассылку'}
    success_message = "Обновления сохранены"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self, **kwargs):
        if self.get_form_class() == ModeratorNewsletterForm:
            return reverse('sender:newsletters_list')
        return reverse("sender:newsletter_detail", kwargs={'pk': self.object.pk})

    def get_form_class(self):
        newsletter = self.get_object(queryset=None)
        logged_user = self.request.user
        if newsletter.owner == logged_user:
            return NewsletterForm
        elif logged_user.has_perm('sender.can_change_newsletter_status'):
            return ModeratorNewsletterForm
        else:
            raise PermissionDenied

    def form_valid(self, form):
        if self.get_form_class() == ModeratorNewsletterForm:
            newsletter = form.save(commit=False)
            if form.cleaned_data['status'] == 'closed':
                newsletter.last_sent = timezone.now()
            newsletter.save()
            return super().form_valid(form)

        return super().form_valid(form)


@method_decorator(cache_page(60 * 5), name='dispatch')
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

    def get_object(self, queryset=None):
        newsletter = super().get_object(queryset)
        user = self.request.user
        if user.is_staff or user == newsletter.owner:
            return newsletter
        raise PermissionDenied

                                                                # MAILINGATTEMPT


class MailingAttemptCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    context_object_name = 'newsletters'
    form_class = MailingAttemptForm
    template_name = 'sender/mailing_create.html'
    success_url = reverse_lazy("sender:mailing_attempts")
    extra_context = {'title': 'Отправить рассылку',
                     }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['headers'] = ['ID', 'Дата старта', 'Дата завершения', 'Текущий статус', 'Сообщение',
                              'Получатели', 'Опции']
        if self.request.user.has_perm('sender.can_view_all_newsletters'):
            newsletters = Newsletter.objects.all()
        else:
            newsletters = UserDataCache.get_user_data(self.request.user, 'newsletters')
        context['newsletters'] = newsletters

        return context

    def form_valid(self, form):
        if form.is_valid():
            attempt = form.save(commit=False)
            newsletter = Newsletter.objects.get(pk=attempt.newsletter.pk)
            success, response = mail_attempt(newsletter)
            if success:
                attempt.exc_state = MailingAttempt.SUCCESSFUL
                attempt.server_response = response
                attempt.save()
                messages.add_message(self.request, messages.SUCCESS, "Рассылка успешно отправлена")
                if newsletter.status == 'created':
                    newsletter.status = 'started'
                    newsletter.first_sent = timezone.now()
                    newsletter.save()
            else:
                attempt.server_response = response
                attempt.save()
                messages.add_message(self.request, messages.ERROR, "Ошибка при отправке рассылки")
        return redirect(self.success_url)


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = 'sender/mailing_attempts.html'
    context_object_name = 'mailings'
    extra_context = {'title': 'Статистика',
                     'header': 'Результаты отправки'
                     }

    def get_context_data(self, **kwargs):
        """Всем группам пользователей позволяет увидеть только свои рассылки"""
        context = super().get_context_data(**kwargs)
        context['headers'] = ['ID', 'Дата старта', 'Дата завершения', 'Текущий статус', 'Сообщение',
                              'Получатели', 'Опции']
        newsletters = UserDataCache.get_user_data(self.request.user, 'newsletters')
        context['newsletters'] = newsletters
        return context

    def get_queryset(self):
        """Менеджеру позволяет увидеть все попытки рассылок, а пользователю только свои"""
        queryset = super().get_queryset()
        user = self.request.user
        if user.has_perm('sender.can_view_all_newsletters'):
            return queryset
        return queryset.filter(newsletter__owner=user)
