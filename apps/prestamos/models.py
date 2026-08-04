from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from catalogo.models import Libro
from usuarios.models import Lector

class Prestamo(models.Model):
    ESTADO_CHOICES = (
        ('Activo', 'Activo'),
        ('Devuelto', 'Devuelto'),
        ('Atrasado', 'Atrasado'),
    )

    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos', verbose_name="Libro")
    lector = models.ForeignKey(Lector, on_delete=models.CASCADE, related_name='prestamos', verbose_name="Lector")
    fecha_prestamo = models.DateField(default=timezone.now, verbose_name="Fecha de Préstamo")
    fecha_limite = models.DateField(verbose_name="Fecha Límite de Devolución")
    fecha_devolucion_real = models.DateField(blank=True, null=True, verbose_name="Fecha de Devolución Real")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Activo', verbose_name="Estado del Préstamo")
    comprobante_pdf = models.FileField(upload_to='comprobantes/', blank=True, null=True, verbose_name="Comprobante PDF")
    codigo_verificacion = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Código de Verificación")
    dias_retraso = models.IntegerField(default=0, verbose_name="Días de Retraso")

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']

    def clean(self):
        super().clean()

        # Validación 1: Verificar copias disponibles (solo al crear nuevo préstamo)
        if not self.pk:
            if self.libro.copias_disponibles <= 0:
                raise ValidationError(f"No hay copias disponibles del libro '{self.libro.titulo}'.")

            # Validación 2: Lector sancionado no puede prestar
            if self.lector.estado == 'Sancionado':
                raise ValidationError(f"El lector {self.lector.user.get_full_name()} se encuentra SANCCIONADO y no puede realizar nuevos préstamos.")

            # Validación 3: Lector con préstamos atrasados
            prestamos_atrasados = Prestamo.objects.filter(
                lector=self.lector,
                estado='Atrasado'
            ).exclude(pk=self.pk).exists()

            if prestamos_atrasados:
                raise ValidationError(f"El lector {self.lector.user.get_full_name()} posee préstamos ATRASADOS pendientes de devolución.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Si no se define fecha límite por defecto, asignar 7 días por defecto
        if not self.fecha_limite:
            self.fecha_limite = (self.fecha_prestamo or timezone.now().date()) + timedelta(days=7)

        # Generar código único de verificación si no existe
        if not self.codigo_verificacion:
            import uuid
            self.codigo_verificacion = f"BIB-{uuid.uuid4().hex[:8].upper()}"

        # Al registrar un préstamo nuevo, descontar 1 copia disponible
        if is_new:
            self.clean()
            self.libro.copias_disponibles -= 1
            self.libro.save()

        super().save(*args, **kwargs)

    def registrar_devolucion(self):
        """Registra la devolución del libro, calcula días de mora y actualiza inventario y estado del lector."""
        if self.estado == 'Devuelto':
            return

        hoy = timezone.now().date()
        self.fecha_devolucion_real = hoy

        if hoy > self.fecha_limite:
            self.dias_retraso = (hoy - self.fecha_limite).days
            self.estado = 'Atrasado'
            # Sancionar al lector por mora
            self.lector.estado = 'Sancionado'
            self.lector.save()
        else:
            self.dias_retraso = 0
            self.estado = 'Devuelto'

        # Reponer 1 copia disponible al catálogo
        self.libro.copias_disponibles += 1
        self.libro.save()
        self.save()
