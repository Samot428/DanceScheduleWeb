from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder": "Username"
        })
    )
    password1 = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "type":"password",
            "placeholder":"Password"
        })
    )
    password2 = forms.CharField(
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "type":"password",
            "placeholder":"Confirm the Password"
        })
    )
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={"class":"form-select"}),
        label="I am a:"
    )

    class Meta:
        model = User
        fields = ('username', 'user_type', 'password1', 'password2')
    
class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"Username"
        })
    )

    password = forms.CharField(
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "type":"password",
            "placeholder":"Password"
        })
    )

    class Meta:
        model = User
        fields = ("username", "password")