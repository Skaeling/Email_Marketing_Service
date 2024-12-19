from django.urls import path
from . import views

app_name = 'sender'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipients/', views.RecipientListView.as_view(), name='recipients_list'),
    path('recipients/create_new/', views.RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/update/<int:pk>/', views.RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/detail/<int:pk>/', views.RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/delete/<int:pk>/', views.RecipientDeleteView.as_view(), name='recipient_confirm_delete'),

    path('messages/', views.MessageListView.as_view(), name='messages_list'),
    path('messages/create_new/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>/', views.MessageUpdateView.as_view(), name='message_update'),
    path('messages/detail/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/delete/<int:pk>/', views.MessageDeleteView.as_view(), name='message_confirm_delete'),

    path('newsletters/', views.NewsletterListView.as_view(), name='newsletters_list'),
    path('newsletters/create_new/', views.NewsletterCreateView.as_view(), name='newsletter_create'),
    path('newsletters/update/<int:pk>/', views.NewsletterUpdateView.as_view(), name='newsletter_update'),
    path('newsletters/detail/<int:pk>/', views.NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletters/delete/<int:pk>/', views.NewsletterDeleteView.as_view(), name='newsletter_confirm_delete'),

    path('mailing_attempts/create_new/', views.MailingAttemptCreateView.as_view(), name='send_mail'),
    path('mailing_attempts/create_new/result/', views.MailingAttemptListView.as_view(), name='mailing_attempts'),

]
