from django import forms
from .models import Prestamo
from catalogo.models import Libro
from usuarios.models import Lector

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['libro', 'lector', 'fecha_limite']
        widgets = {
            'libro': forms.Select(attrs={'class': 'form-select'}),
            'lector': forms.Select(attrs={'class': 'form-select'}),
            'fecha_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo libros con copias disponibles
        self.fields['libro'].queryset = Libro.objects.filter(copias_disponibles__gt=0)
        # Mostrar solo lectores habilitados
        self.fields['lector'].queryset = Lector.objects.filter(estado='Habilitado')
