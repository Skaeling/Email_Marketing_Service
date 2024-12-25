from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from django import forms
from .models import Recipient, Message, Newsletter, MailingAttempt


class CustomCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('', *self.fields, css_class='form-control border-primary', style='font-size: 13px;'),
            Row(
                Column(HTML(
                    '<a class="btn btn-outline-primary form-group" href="javascript:history.back()">Назад</a>')),
                Column(Submit('submit', '{% if object %}Сохранить{% else %}Ок{% endif %}',
                              css_class='btn btn-primary form-group')),
                css_class='col-12 mt-2 text-center'
            )
        )


class RecipientForm(CustomCreateForm):
    class Meta:
        model = Recipient
        exclude = ('creator',)


class MessageForm(CustomCreateForm):
    class Meta:
        model = Message
        exclude = ('author',)


class NewsletterForm(CustomCreateForm):
    class Meta:
        model = Newsletter
        exclude = ('status',
                   'owner',
                   )
        labels = {'message': 'Сообщение',
                  'recipients': 'Получатели',
                  }
        widgets = {
            'first_sent': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
            'last_sent': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

        if self.request.user.has_perm('sender.can_view_all_messages') and self.request.user.has_perm(
                'sender.can_view_all_clients'):
            self.fields['recipients'].queryset = Recipient.objects.all()
            self.fields['message'].queryset = Message.objects.all()
        else:
            self.fields['recipients'].queryset = Recipient.objects.filter(creator=self.request.user)
            self.fields['message'].queryset = Message.objects.filter(author=self.request.user)
        self.fields['first_sent'].help_text = 'Без указания даты отправка рассылки будет доступна только вручную'
        self.fields['last_sent'].help_text = 'Без указания даты отправка рассылки будет доступна только вручную'



class ModeratorNewsletterForm(CustomCreateForm):
    class Meta:
        model = Newsletter
        fields = ('status',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)


class MailingAttemptForm(CustomCreateForm):
    class Meta:
        model = MailingAttempt
        fields = ('newsletter',)
        labels = {'newsletter': 'Номер рассылки',
                  }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        if self.request.user.has_perm('sender.can_view_all_newsletters'):
            self.fields['newsletter'].queryset = Newsletter.objects.all()
        else:
            self.fields['newsletter'].queryset = Newsletter.objects.filter(owner=self.request.user)
