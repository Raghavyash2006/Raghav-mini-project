from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class AuthFormMixin:
    field_placeholders = {}

    def _apply_field_styles(self):
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} auth-input".strip()
            field.widget.attrs.setdefault("autocomplete", field_name)
            placeholder = self.field_placeholders.get(field_name)
            if placeholder:
                field.widget.attrs.setdefault("placeholder", placeholder)


class LoginForm(AuthFormMixin, AuthenticationForm):
    field_placeholders = {
        "username": "Enter your username",
        "password": "Enter your password",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self._apply_field_styles()


class SignupForm(AuthFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    field_placeholders = {
        "username": "Choose a username",
        "email": "Enter your email address",
        "password1": "Create a password",
        "password2": "Repeat the password",
    }

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_field_styles()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user