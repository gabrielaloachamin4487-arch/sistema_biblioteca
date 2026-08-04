import os
from django.db import models
from django.core.exceptions import ValidationError

def validar_tamano_pdf(value):
    """Validación de negocio: El PDF de muestra no debe superar los 8 MB (8 * 1024 * 1024 bytes)."""
    limite_bytes = 8 * 1024 * 1024
    if value.size > limite_bytes:
        size_mb = value.size / (1024 * 1024)
        raise ValidationError(f"El archivo PDF de muestra pesa {size_mb:.2f} MB. No debe superar los 8 MB.")
    
    extension = os.path.splitext(value.name)[1].lower()
    if extension != '.pdf':
        raise ValidationError("La muestra solo admite archivos en formato PDF.")

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título")
    autor = models.CharField(max_length=200, verbose_name="Autor")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name="libros", verbose_name="Categoría")
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True, verbose_name="Portada (Imagen)")
    muestra_pdf = models.FileField(
        upload_to='muestras/',
        blank=True,
        null=True,
        validators=[validar_tamano_pdf],
        verbose_name="Muestra / Resumen PDF (Máx 8 MB)"
    )
    cantidad_total = models.PositiveIntegerField(default=1, verbose_name="Cantidad Total de Copias")
    copias_disponibles = models.PositiveIntegerField(default=1, verbose_name="Copias Disponibles")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['titulo']

    def clean(self):
        super().clean()
        if self.copias_disponibles > self.cantidad_total:
            raise ValidationError({
                'copias_disponibles': "Las copias disponibles no pueden exceder la cantidad total de copias."
            })

    def save(self, *args, **kwargs):
        # Al crear por primera vez si no se especifica copias_disponibles
        if not self.pk and self.copias_disponibles == 1 and self.cantidad_total > 1:
            self.copias_disponibles = self.cantidad_total
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} - {self.autor} (ISBN: {self.isbn})"
