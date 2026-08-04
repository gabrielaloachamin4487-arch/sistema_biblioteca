from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from catalogo.models import Libro
from usuarios.models import Lector
from prestamos.models import Prestamo

@login_required
def dashboard(request):
    """Panel principal de control (Dashboard) con métricas clave y accesos directos."""
    total_libros = Libro.objects.count()
    total_copias = Libro.objects.aggregate(total=Sum('cantidad_total'))['total'] or 0
    copias_disponibles = Libro.objects.aggregate(total=Sum('copias_disponibles'))['total'] or 0
    total_lectores = Lector.objects.count()
    
    prestamos_activos = Prestamo.objects.filter(estado='Activo').count()
    prestamos_atrasados = Prestamo.objects.filter(estado='Atrasado').count()
    lectores_sancionados = Lector.objects.filter(estado='Sancionado').count()

    libros_recientes = Libro.objects.all().order_by('-fecha_creacion')[:6]
    
    is_bibliotecario = request.user.is_staff or request.user.is_superuser

    if not is_bibliotecario and hasattr(request.user, 'lector_profile'):
        mis_prestamos = Prestamo.objects.filter(lector=request.user.lector_profile).order_by('-fecha_prestamo')[:5]
    else:
        mis_prestamos = None

    context = {
        'total_libros': total_libros,
        'total_copias': total_copias,
        'copias_disponibles': copias_disponibles,
        'total_lectores': total_lectores,
        'prestamos_activos': prestamos_activos,
        'prestamos_atrasados': prestamos_atrasados,
        'lectores_sancionados': lectores_sancionados,
        'libros_recientes': libros_recientes,
        'mis_prestamos': mis_prestamos,
        'is_bibliotecario': is_bibliotecario,
    }
    return render(request, 'core/dashboard.html', context)
