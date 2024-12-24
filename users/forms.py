from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm


class StyleFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('', *self.fields, css_class='form-control border-primary', style='font-size: 13px;'),
            Row(
                Column(HTML('<a class="btn btn-outline-primary form-group" href="javascript:history.back()">Назад</a>')),
                Column(Submit('submit', '{% if object %}Сохранить{% else %}ОК{% endif %}', css_class='btn btn-primary form-group')),
                css_class='col-12 mt-2 text-center'
            )
        )


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
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
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = 'Введите пароль еще раз для подтверждения.'


class CustomLoginForm(StyleFormMixin, AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')


class CustomUpdateForm(StyleFormMixin, UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'country', 'avatar',)
        labels = {
            'phone_number': 'Номер телефона',
            'country': 'Страна проживания',
            'avatar': 'Аватар'
        }


class ModeratorUpdateForm(StyleFormMixin, UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ('is_active',
                  )
