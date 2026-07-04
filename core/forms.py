from django import forms
from django.contrib.auth import get_user_model

from .models import Application, Job

User = get_user_model()

ROLE_CHOICES = (
    ("seeker", "Job Seeker"),
    ("employer", "Employer"),
)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    company = forms.CharField(max_length=150, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title", "job_type", "company", "location", "category",
            "salary", "description", "requirements",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cover_letter"]
        widgets = {
            "cover_letter": forms.Textarea(attrs={"rows": 8}),
        }
