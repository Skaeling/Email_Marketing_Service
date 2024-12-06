from django.urls import path

from .forms import CustomLoginForm
from .views import RegisterView
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'users'

urlpatterns = [
    path('users/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html', authentication_form=CustomLoginForm),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='sender:home'), name='logout'),

]
