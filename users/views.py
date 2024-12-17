from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetView, PasswordContextMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
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


class CustomUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    extra_context = {'title': 'Пользователи'}
    permission_required = 'users.view_customuser'

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     group_name = 'Пользователи'
    #     group = Group.objects.get(name=group_name)
    #     users = queryset.filter(groups=group)
    #     return users

    def get_queryset(self):
        queryset = super().get_queryset()
        users = queryset.filter(groups__id=1)
        return users


class CustomUserDetailView(PermissionRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    extra_context = {'title': 'Профиль пользователя'}
    permission_required = 'users.view_customuser'


class CustomUserUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = CustomUpdateForm
    template_name = 'users/register.html'
    context_object_name = 'user'
    success_message = "Профиль успешно обновлен!"
    extra_context = {'title': 'Редактировать профиль'}
    permission_required = 'users.change_customuser'

    def get_success_url(self, **kwargs):
        return reverse("users:user_detail", kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        logged_user = self.request.user
        if not logged_user.has_perm('users.can_change_user') and user != logged_user:
            raise PermissionDenied
        return user


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_message = "На указанную вами почту направлена инструкция по сбросу пароля, " \
                      " Если вы не получили письмо, проверьте папку спам."
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