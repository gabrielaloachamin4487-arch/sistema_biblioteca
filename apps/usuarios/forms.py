from django import forms
from .models import Lector # O el modelo que estés utilizando

class LectorForm(forms.ModelForm):
    class Meta:
        model = Lector # Cambia por tu modelo real
        fields = ['username', 'first_name', 'last_name', 'email', 'password'] # Ajusta según tus campos
        
        # 1. Traducir etiquetas al español
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'password': 'Contraseña',
        }
        
        # 2. Agregar máscaras o texto de guía (placeholders)
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Ej. juan_perez'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Ej. Juan Carlos'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Ej. Pérez Gómez'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ej. correo@ejemplo.com'}),
            'password': forms.PasswordInput(attrs={'placeholder': '********'}),
        }