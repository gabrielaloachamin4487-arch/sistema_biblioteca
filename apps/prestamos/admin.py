from django.contrib import admin
from .models import Prestamo

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('codigo_verificacion', 'libro', 'lector', 'fecha_prestamo', 'fecha_limite', 'estado', 'dias_retraso')
    list_filter = ('estado', 'fecha_prestamo', 'fecha_limite')
    search_fields = ('codigo_verificacion', 'libro__titulo', 'lector__codigo_institucional', 'lector__user__username')
