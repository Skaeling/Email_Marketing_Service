from django.shortcuts import render
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Recipient, Message, Newsletter
from django.urls import reverse_lazy, reverse


def home(request):
    clients = Recipient.objects.order_by('email').distinct('email')
    all_mailings = Newsletter.objects.count()
    active_mailings = Newsletter.objects.filter(status=Newsletter.STARTED)
    result = active_mailings.count()
    extra_context = {'title': 'Главная',
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
    fields = ['email', 'fullname', 'comment']
    template_name = 'sender/recipient_create.html'
    context_object_name = 'client'
    extra_context = {'title': 'Создать получателя'}


class RecipientUpdateView(UpdateView):
    model = Recipient
    fields = ['email', 'fullname', 'comment']
    template_name = 'sender/recipient_create.html'
    context_object_name = 'client'
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
    template_name = 'sender/recipient_confirm_delete.html'
    context_object_name = 'client'
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
    fields = ['title', 'body']
    template_name = 'sender/message_create.html'
    context_object_name = 'message'
    extra_context = {'title': 'Создать сообщение'}


class MessageUpdateView(UpdateView):
    model = Message
    fields = ['title', 'body']
    template_name = 'sender/message_create.html'
    context_object_name = 'message'
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
    template_name = 'sender/message_confirm_delete.html'
    context_object_name = 'message'
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
    fields = ['status', 'message', 'recipients']
    template_name = 'sender/newsletter_create.html'
    context_object_name = 'newsletter'
    extra_context = {'title': 'Создать рассылку'}

    def get_success_url(self, **kwargs):
        return reverse("sender:newsletter_detail", kwargs={'pk': self.object.pk})


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    fields = ['status', 'message', 'recipients']
    template_name = 'sender/newsletter_create.html'
    context_object_name = 'newsletter'
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
    template_name = 'sender/newsletter_confirm_delete.html'
    context_object_name = 'newsletter'
    extra_context = {'title': 'Удаление рассылку'}
    success_url = reverse_lazy('sender:newsletters_list')