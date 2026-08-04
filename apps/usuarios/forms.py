from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Lector

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Nombre de usuario o código'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Contraseña'
    }))

class LectorRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Lector
        fields = ['codigo_institucional', 'tipo', 'foto_carne', 'estado']
        widgets = {
            'codigo_institucional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. EST-2026-001'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'foto_carne': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está registrado.")
        return username

class LectorUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Lector
        fields = ['codigo_institucional', 'tipo', 'foto_carne', 'estado']
        widgets = {
            'codigo_institucional': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'foto_carne': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
