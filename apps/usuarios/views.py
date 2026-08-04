from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Lector
from .forms import CustomLoginForm, LectorRegistrationForm, LectorUpdateForm

def bibliotecario_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def login_view(request):
    """Vista de Login institucional."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Bienvenido(a), {user.get_full_name() or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = CustomLoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    """Vista de Logout."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')

@login_required
def lector_list(request):
    """Lista de lectores registrados (Solo Bibliotecarios)."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Acceso restringido a administradores de biblioteca.")
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')

    lectores = Lector.objects.select_related('user').all()

    if query:
        lectores = lectores.filter(
            user__first_name__icontains=query) | lectores.filter(
            user__last_name__icontains=query) | lectores.filter(
            codigo_institucional__icontains=query) | lectores.filter(
            user__username__icontains=query)

    if tipo:
        lectores = lectores.filter(tipo=tipo)

    if estado:
        lectores = lectores.filter(estado=estado)

    context = {
        'lectores': lectores,
        'query': query,
        'tipo': tipo,
        'estado': estado,
    }
    return render(request, 'usuarios/lector_list.html', context)

@login_required
def lector_create(request):
    """Registro de nuevo lector (Estudiante/Docente)."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Solo el Bibliotecario puede registrar lectores.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = LectorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            lector = form.save(commit=False)
            lector.user = user
            lector.save()
            messages.success(request, f"Lector '{user.get_full_name()}' registrado con éxito.")
            return redirect('lector_list')
    else:
        form = LectorRegistrationForm()

    return render(request, 'usuarios/lector_form.html', {'form': form, 'titulo_pagina': 'Registrar Nuevo Lector'})

@login_required
def lector_update(request, pk):
    """Edición de perfil y cambio de estado (Habilitado/Sancionado)."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    lector = get_object_or_404(Lector, pk=pk)
    if request.method == 'POST':
        form = LectorUpdateForm(request.POST, request.FILES, instance=lector)
        if form.is_valid():
            lector.user.first_name = form.cleaned_data['first_name']
            lector.user.last_name = form.cleaned_data['last_name']
            lector.user.email = form.cleaned_data['email']
            lector.user.save()
            form.save()
            messages.success(request, f"Perfil del lector '{lector.user.get_full_name()}' actualizado.")
            return redirect('lector_list')
    else:
        initial = {
            'first_name': lector.user.first_name,
            'last_name': lector.user.last_name,
            'email': lector.user.email,
        }
        form = LectorUpdateForm(instance=lector, initial=initial)

    return render(request, 'usuarios/lector_form.html', {
        'form': form,
        'lector': lector,
        'titulo_pagina': f'Editar Lector: {lector.user.get_full_name()}'
    })
