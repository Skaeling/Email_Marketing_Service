from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordContextMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect

from .forms import CustomUserCreationForm, CustomUpdateForm
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse

from .models import CustomUser


class RegisterView(CreateView):
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация нового пользователя'}
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно!")
        return super().form_valid(form)


class CustomUserDetailView(DetailView):
    model = CustomUser
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    extra_context = {'title': 'Профиль пользователя'}


class CustomUserUpdateView(SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = CustomUpdateForm
    template_name = 'users/register.html'
    context_object_name = 'user'
    success_message = "Профиль успешно обновлен!"
    extra_context = {'title': 'Редактировать профиль'}

    def get_success_url(self, **kwargs):
        return reverse("users:user_detail", kwargs={'pk': self.object.pk})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('sender:home')


# class PasswordResetView(PasswordContextMixin, FormView):
#     """
#    success_url = reverse_lazy("{app_name}:password_reset_done")
#     """
#
#
# class PasswordResetConfirmView(PasswordContextMixin, FormView):
#    """
#    success_url = reverse_lazy("{app_name}:password_reset_complete")
#    """