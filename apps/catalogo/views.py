from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Libro, Categoria
from .forms import LibroForm, CategoriaForm

def bibliotecario_required(user):
    """Auxiliar para verificar si el usuario es staff/bibliotecario."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
def libro_list(request):
    """Vista del catálogo de libros en tarjetas responsivas con buscador."""
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')
    solo_disponibles = request.GET.get('disponibles', '') == '1'

    libros = Libro.objects.all().select_related('categoria')

    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(isbn__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )

    if categoria_id and categoria_id.isdigit():
        libros = libros.filter(categoria_id=int(categoria_id))

    if solo_disponibles:
        libros = libros.filter(copias_disponibles__gt=0)

    categorias = Categoria.objects.all()

    context = {
        'libros': libros,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
        'solo_disponibles': solo_disponibles,
        'es_bibliotecario': bibliotecario_required(request.user),
    }
    return render(request, 'catalogo/libro_list.html', context)

@login_required
def libro_detail(request, pk):
    """Detalle de un libro específico con visor/descarga de muestra PDF."""
    libro = get_object_or_404(Libro.objects.select_related('categoria'), pk=pk)
    context = {
        'libro': libro,
        'es_bibliotecario': bibliotecario_required(request.user),
    }
    return render(request, 'catalogo/libro_detail.html', context)

@login_required
def libro_create(request):
    """Creación de un nuevo libro (Solo Bibliotecarios)."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Acceso no autorizado. Solo el Bibliotecario puede gestionar libros.")
        return redirect('libro_list')

    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save()
            messages.success(request, f"El libro '{libro.titulo}' ha sido registrado exitosamente.")
            return redirect('libro_detail', pk=libro.pk)
    else:
        form = LibroForm()

    return render(request, 'catalogo/libro_form.html', {'form': form, 'titulo_pagina': 'Registrar Nuevo Libro'})

@login_required
def libro_update(request, pk):
    """Actualización de un libro (Solo Bibliotecarios)."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Acceso no autorizado. Solo el Bibliotecario puede actualizar libros.")
        return redirect('libro_list')

    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, f"El libro '{libro.titulo}' ha sido actualizado.")
            return redirect('libro_detail', pk=libro.pk)
    else:
        form = LibroForm(instance=libro)

    return render(request, 'catalogo/libro_form.html', {
        'form': form,
        'libro': libro,
        'titulo_pagina': f'Editar Libro: {libro.titulo}'
    })

@login_required
def libro_delete(request, pk):
    """Eliminación de un libro (Solo Bibliotecarios)."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('libro_list')

    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        titulo = libro.titulo
        libro.delete()
        messages.success(request, f"El libro '{titulo}' ha sido eliminado del catálogo.")
        return redirect('libro_list')

    return render(request, 'catalogo/libro_confirm_delete.html', {'libro': libro})
