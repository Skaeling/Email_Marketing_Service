from django.urls import path, reverse_lazy

from .views import RegisterView, CustomLoginView, CustomUserDetailView, CustomUserUpdateView, ResetPasswordView, \
    CustomUserListView, email_verification
from django.contrib.auth.views import LogoutView, PasswordResetConfirmView, PasswordResetCompleteView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm-email/<str:token>/', email_verification, name='confirm-email'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='sender:home'), name='logout'),
    path('profiles_list/', CustomUserListView.as_view(), name='user_list'),
    path('profile/<int:pk>/', CustomUserDetailView.as_view(), name='user_detail'),
    path('profile/update/<int:pk>/', CustomUserUpdateView.as_view(), name='user_update'),
    path('password_reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password_reset_confirm/<str:uidb64>/<str:token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          success_url=reverse_lazy("users:password_reset_complete")),
         name='password_reset_confirm'),
    path('password_reset_complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

]
