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
    user_sex = forms.ChoiceField(
        choices=UserProfile.USER_SEX_CHOICES,
        widget=forms.Select(attrs={"class":"form-select"}),
        label="Sex:"
        )
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={"class":"form-select"}),
        label="I am a:"
    )

    # if user_type == 'trainer' these options will be shown
    trainer_focus = forms.ChoiceField(
        choices=UserProfile.TRAINER_FOCUS_CHOICES,
        widget=forms.Select(attrs={"class":"form-select"}),
        label='My Focus:'
    )

    # otherwise if user_type == 'dancer' these options will be shown
    dancer_class_stt = forms.ChoiceField(
        choices=UserProfile.DANCER_CLASS,
        widget=forms.Select(attrs={"class":"form-select"}),
        label='STT',
    )

    dancer_class_lat = forms.ChoiceField(
        choices=UserProfile.DANCER_CLASS,
        widget=forms.Select(attrs={"class":"form-select"}),
        label='LAT',
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