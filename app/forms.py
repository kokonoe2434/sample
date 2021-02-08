from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from . import utils

User = get_user_model()


class CustomUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class CustomLoginForm(AuthenticationForm):
    """カスタムログインフォーム"""
    token = forms.CharField(max_length=254, label="Google Authenticator OTP")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def confirm_login_allowed(self, user):
        """二要素認証チェック"""
        if utils.get_token(user) != self.cleaned_data.get('token'):
            raise forms.ValidationError(
                "'Google Authenticator OTP' is invalid."
            )
        super().confirm_login_allowed(user)