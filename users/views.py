import secrets

from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from config.settings import DEFAULT_FROM_EMAIL

from .forms import (CustomLoginForm, CustomUpdateForm, CustomUserCreationForm,
                    ModeratorUpdateForm)
from .models import CustomUser


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация нового пользователя'}
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('sender:home')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/confirm-email/{token}/'
        send_mail(
            subject='Подтверждение адреса электронной почты',
            message=f'Перейдите по ссылке для активации вашего профиля Send-or-Treat {url}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        messages.success(self.request,
                         "Ваша регистрация прошла успешно."
                         "Ссылка для активации профиля направлена на указанный электронный адрес")
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse('users:login'))


class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = 'users/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    extra_context = {'title': 'Авторизация'}
    success_message = 'Вы успешно вошли в систему!'

    def form_invalid(self, form):
        email = form.cleaned_data.get('username')
        user = get_object_or_404(CustomUser, email=email)

        if not user.is_active:
            form.add_error(None, 'Ваш аккаунт неактивен. Если вы заходите на сайт впервые - '
                                 'подтвердите email согласно инструкции на вашей почте')
        return self.render_to_response(self.get_context_data(form=form))


class CustomUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    extra_context = {'title': 'Пользователи'}
    permission_required = 'users.can_view_all_users'

    def get_queryset(self):
        queryset = super().get_queryset()
        users = queryset.exclude(username='admin').exclude(groups__name='Менеджеры')
        return users


class CustomUserDetailView(DetailView):
    model = CustomUser
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    extra_context = {'title': 'Профиль пользователя'}

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        logged_user = self.request.user
        if user == logged_user or logged_user.has_perm('users.can_view_all_users'):
            return user
        raise PermissionDenied


class CustomUserUpdateView(SuccessMessageMixin, UpdateView):
    model = CustomUser
    template_name = 'users/register.html'
    context_object_name = 'user'
    success_message = "Обновления сохранены"
    extra_context = {'title': 'Редактировать профиль'}

    def get_form_class(self):
        user = self.get_object(queryset=None)
        logged_user = self.request.user
        if user == logged_user:
            return CustomUpdateForm
        elif logged_user.has_perm('users.can_block_user'):
            return ModeratorUpdateForm
        else:
            raise PermissionDenied

    def get_success_url(self, **kwargs):
        if self.get_form_class() == ModeratorUpdateForm:
            return reverse('users:user_list')
        return reverse("users:user_detail", kwargs={'pk': self.object.pk})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_message = "На указанную вами почту направлена инструкция по сбросу пароля. " \
                      " Если вы не получили письмо, проверьте папку спам."
    success_url = reverse_lazy('sender:home')
