from django import forms
from .models import Libro, Categoria

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'isbn', 'categoria', 'portada', 'muestra_pdf', 'cantidad_total', 'copias_disponibles']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Cien Años de Soledad'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Gabriel García Márquez'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 978-0307474728'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'portada': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'muestra_pdf': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'cantidad_total': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'copias_disponibles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Literatura, Ciencias'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
