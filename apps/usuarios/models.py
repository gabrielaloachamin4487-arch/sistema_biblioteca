from django.db import models
from django.contrib.auth.models import User

class Lector(models.Model):
    TIPO_CHOICES = (
        ('Estudiante', 'Estudiante'),
        ('Docente', 'Docente'),
    )
    ESTADO_CHOICES = (
        ('Habilitado', 'Habilitado'),
        ('Sancionado', 'Sancionado'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lector_profile', verbose_name="Usuario de Sistema")
    codigo_institucional = models.CharField(max_length=50, unique=True, verbose_name="Código Institucional")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Estudiante', verbose_name="Tipo de Lector")
    foto_carne = models.ImageField(upload_to='carnes/', blank=True, null=True, verbose_name="Foto de Carné")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Habilitado', verbose_name="Estado de Cuenta")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lector"
        verbose_name_plural = "Lectores"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        nombre_completo = self.user.get_full_name() or self.user.username
        return f"{nombre_completo} ({self.codigo_institucional}) - {self.tipo} [{self.estado}]"

    @property
    def es_sancionado(self):
        return self.estado == 'Sancionado'
