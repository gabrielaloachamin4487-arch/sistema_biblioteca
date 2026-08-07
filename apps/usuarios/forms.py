from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Lector


# 1. Formulario de Inicio de Sesión
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


# 2. Formulario de Registro de Lectores
class LectorRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. juan_perez'
        })
    )
    first_name = forms.CharField(
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. Juan Carlos'
        })
    )
    last_name = forms.CharField(
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. Pérez Gómez'
        })
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. correo@ejemplo.com'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '********'
        })
    )

    class Meta:
        model = Lector
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asigna la clase form-control a todos los campos para no romper el diseño oscuro
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


# 3. Formulario de Edición/Actualización
class LectorUpdateForm(forms.ModelForm):
    class Meta:
        model = Lector
        fields = '__all__'