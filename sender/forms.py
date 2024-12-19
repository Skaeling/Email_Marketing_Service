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
                Column(HTML('<a class="btn btn-lg btn-outline-primary form-group" href="javascript:history.back()">Назад</a>')),
                Column(Submit('submit', '{% if object %}Сохранить{% else %}Создать{% endif %}',
                              css_class='btn btn-lg btn-outline-primary form-group')), css_class='col-12 mt-2 text-center'
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
        exclude = ('status', 'first_sent', 'last_sent', 'owner',)
        labels = {'message': 'Рассылка',
                  'recipients': 'Получатели',
                  }


class MailingAttemptForm(CustomCreateForm):
    class Meta:
        model = MailingAttempt
        fields = ('newsletter',)
