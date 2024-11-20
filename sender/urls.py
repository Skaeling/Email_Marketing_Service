from django.urls import path
from sender import views
from sender.views import RecipientListView, RecipientCreateView, RecipientUpdateView, RecipientDetailView, RecipientDeleteView

app_name = 'sender'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipients/', RecipientListView.as_view(), name='recipients_list'),
    path('recipients/create_new/', RecipientCreateView.as_view(), name='create_recipient'),
    path('recipients/update/<int:pk>/', RecipientUpdateView.as_view(), name='update_recipient'),
    path('recipients/detail/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/delete/<int:pk>/', RecipientDeleteView.as_view(), name='recipient_confirm_delete'),

]