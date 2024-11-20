from django.urls import path
from sender import views
from sender.views import RecipientListView, RecipientCreateView, RecipientUpdateView, RecipientDetailView, \
    RecipientDeleteView, MessageListView, MessageCreateView, MessageDeleteView, MessageDetailView, MessageUpdateView

app_name = 'sender'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipients/', RecipientListView.as_view(), name='recipients_list'),
    path('recipients/create_new/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/update/<int:pk>/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/detail/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/delete/<int:pk>/', RecipientDeleteView.as_view(), name='recipient_confirm_delete'),

    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('messages/create_new/', MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/detail/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='message_confirm_delete'),
]
