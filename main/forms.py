from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="I am a:"
    )

    class Meta:
        model = User
        fields = ('username', 'user_type', 'password1', 'password2')