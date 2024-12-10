from .forms import CustomUserCreationForm
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy


class RegisterView(CreateView):
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация нового пользователя'}
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('sender:home')
