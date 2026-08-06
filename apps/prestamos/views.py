from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import Prestamo
from .forms import PrestamoForm
from .utils_pdf import generar_comprobante_pdf
from .utils_reports import exportar_inventario_excel, exportar_morosos_excel, exportar_morosos_csv

def bibliotecario_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
def enviar_correo_directo(request, pk):
    """Permite al Bibliotecario enviar un correo electrónico directo al lector de un préstamo."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('prestamo_list')

    prestamo = get_object_or_404(Prestamo.objects.select_related('lector__user', 'libro'), pk=pk)
    email_lector = prestamo.lector.user.email

    if not email_lector:
        messages.error(request, f"El lector {prestamo.lector.user.get_full_name()} no tiene una dirección de correo configurada.")
        return redirect(request.META.get('HTTP_REFERER', 'prestamo_list'))

    nombre_lector = prestamo.lector.user.get_full_name() or prestamo.lector.user.username

    if prestamo.estado == 'Atrasado':
        asunto = f"⚠️ ALERTA DE INFRACCIÓN: Préstamo Vencido - {prestamo.libro.titulo}"
        mensaje = (
            f"Estimado(a) {nombre_lector},\n\n"
            f"Te notificamos que tu préstamo del libro '{prestamo.libro.titulo}' presenta un retraso.\n"
            f"- Fecha Límite de Devolución: {prestamo.fecha_limite.strftime('%d/%m/%Y')}\n"
            f"- Código de Comprobante: {prestamo.codigo_verificacion}\n\n"
            f"Tu cuenta se encuentra temporalmente SANCIONADA. Por favor acércate a la biblioteca a la brevedad "
            f"para realizar la entrega del ejemplar y regularizar tu estado.\n\n"
            f"Atentamente,\nDirección de Biblioteca Institucional"
        )
    else:
        asunto = f"📖 Recordatorio de Préstamo de Biblioteca: {prestamo.libro.titulo}"
        mensaje = (
            f"Hola {nombre_lector},\n\n"
            f"Te enviamos un recordatorio sobre el préstamo activo del recurso bibliográfico:\n"
            f"- Libro: '{prestamo.libro.titulo}'\n"
            f"- Fecha Límite de Devolución: {prestamo.fecha_limite.strftime('%d/%m/%Y')}\n"
            f"- Código de Comprobante: {prestamo.codigo_verificacion}\n\n"
            f"Por favor recuerda realizar la devolución a tiempo para mantener tu cuenta habilitada.\n\n"
            f"Atentamente,\nBiblioteca Institucional"
        )

    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [email_lector],
            fail_silently=False
        )
        messages.success(request, f"¡Correo enviado exitosamente a {nombre_lector} ({email_lector})!")
    except Exception as e:
        messages.error(request, f"Error de conexión SMTP al enviar el correo a {email_lector}: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'prestamo_list'))


@login_required
def prestamo_list(request):
    """Lista de préstamos. Los lectores ven solo los suyos, los bibliotecarios ven todos."""
    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')

    if bibliotecario_required(request.user):
        prestamos = Prestamo.objects.select_related('libro', 'lector__user').all()
    else:
        # Lector normal
        if hasattr(request.user, 'lector_profile'):
            prestamos = Prestamo.objects.filter(lector=request.user.lector_profile).select_related('libro', 'lector__user')
        else:
            prestamos = Prestamo.objects.none()

    if query:
        prestamos = prestamos.filter(
            libro__titulo__icontains=query) | prestamos.filter(
            lector__codigo_institucional__icontains=query) | prestamos.filter(
            lector__user__first_name__icontains=query)

    if estado:
        prestamos = prestamos.filter(estado=estado)

    # Actualización preventiva de moras
    hoy = timezone.now().date()
    for p in prestamos.filter(estado='Activo'):
        if hoy > p.fecha_limite:
            p.estado = 'Atrasado'
            p.dias_retraso = (hoy - p.fecha_limite).days
            p.lector.estado = 'Sancionado'
            p.lector.save()
            p.save()

    context = {
        'prestamos': prestamos,
        'query': query,
        'estado': estado,
        'es_bibliotecario': bibliotecario_required(request.user),
    }
    return render(request, 'prestamos/prestamo_list.html', context)

@login_required
def prestamo_create(request):
    """Registro de préstamo por el Bibliotecario (o solicitud por lector)."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Solo el Bibliotecario puede autorizar y registrar préstamos.")
        return redirect('prestamo_list')

    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            try:
                # 1. Guardar el préstamo en la base de datos de Neon primero
                prestamo = form.save()
                
                # 2. Intentar generar el comprobante PDF en un bloque seguro
                try:
                    generar_comprobante_pdf(prestamo)
                except (FileNotFoundError, OSError, Exception) as pdf_err:
                    # Si falla por archivo no encontrado en el almacenamiento temporal de Render,
                    # se notifica pero no se interrumpe la creación del préstamo.
                    messages.warning(
                        request, 
                        f"Préstamo registrado correctamente en la base de datos, "
                        f"pero no se pudo adjuntar el archivo físico del PDF ({pdf_err})."
                    )

                messages.success(
                    request, 
                    f"Préstamo autorizado y registrado exitosamente. Código de comprobante: {prestamo.codigo_verificacion}"
                )
                return redirect('prestamo_list')

            except Exception as e:
                messages.error(request, f"Error al procesar el préstamo: {e}")
    else:
        # Pre-seleccionar fecha límite a 7 días
        fecha_default = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        form = PrestamoForm(initial={'fecha_limite': fecha_default})

    return render(request, 'prestamos/prestamo_form.html', {'form': form, 'titulo_pagina': 'Registrar Préstamo de Libro'})

@login_required
def prestamo_devolucion(request, pk):
    """Marcar la devolución de un libro y calcular mora si aplica."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Operación reservada para el Bibliotecario.")
        return redirect('prestamo_list')

    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == 'POST':
        prestamo.registrar_devolucion()
        if prestamo.dias_retraso > 0:
            messages.warning(request, f"Devolución registrada con {prestamo.dias_retraso} día(s) de mora. El lector ha sido sancionado.")
        else:
            messages.success(request, f"Devolución del libro '{prestamo.libro.titulo}' procesada a tiempo.")
        return redirect('prestamo_list')

    return render(request, 'prestamos/prestamo_devolucion_confirm.html', {'prestamo': prestamo})

@login_required
def morosos_list(request):
    """Panel de Lectores Morosos y Préstamos Atrasados."""
    if not bibliotecario_required(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    hoy = timezone.now().date()
    # Actualizar estados atrasados
    activos = Prestamo.objects.filter(estado='Activo', fecha_limite__lt=hoy)
    for p in activos:
        p.estado = 'Atrasado'
        p.dias_retraso = (hoy - p.fecha_limite).days
        p.lector.estado = 'Sancionado'
        p.lector.save()
        p.save()

    morosos = Prestamo.objects.filter(estado='Atrasado').select_related('libro', 'lector__user')
    return render(request, 'prestamos/morosos_list.html', {'morosos': morosos})

@login_required
def exportar_inventario(request):
    if not bibliotecario_required(request.user):
        return redirect('dashboard')
    return exportar_inventario_excel()

@login_required
def exportar_morosos_excel_view(request):
    if not bibliotecario_required(request.user):
        return redirect('dashboard')
    return exportar_morosos_excel()

@login_required
def exportar_morosos_csv_view(request):
    if not bibliotecario_required(request.user):
        return redirect('dashboard')
    return exportar_morosos_csv()
