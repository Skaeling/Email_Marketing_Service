from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    usable_password = None

    class Meta:
        model = CustomUser
        fields = (
            'email', 'username', 'first_name', 'last_name', 'phone_number', 'country', 'avatar', 'password1',
            'password2')
        labels = {
            'phone_number': 'Номер телефона',
            'country': 'Страна проживания',
            'avatar': 'Аватар'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('', *self.fields, css_class='form-control border-primary', style='font-size: 13px;'),
            Row(
                Column(HTML('<a class="btn btn-lg btn-primary form-group" href="javascript:history.back()">Назад</a>')),
                Column(Submit('submit', 'Сохранить', css_class='btn btn-lg btn-primary form-group')),
                css_class='col-12 mt-2 text-center'
            )
        )


class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('', *self.fields, css_class='form-control border-primary', style='font-size: 13px;'),
            Row(
                Column(HTML('<a class="btn btn-primary form-group" href="javascript:history.back()">Назад</a>')),
                Column(Submit('submit', 'Сохранить', css_class='btn btn-primary form-group')),
                css_class='col-12 mt-2 text-center'
            )
        )