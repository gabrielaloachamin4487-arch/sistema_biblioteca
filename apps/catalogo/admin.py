from django.contrib import admin
from .models import Libro, Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'isbn', 'categoria', 'cantidad_total', 'copias_disponibles', 'fecha_creacion')
    list_filter = ('categoria', 'copias_disponibles')
    search_fields = ('titulo', 'autor', 'isbn')
