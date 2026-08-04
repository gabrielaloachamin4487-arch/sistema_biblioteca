from django.contrib import admin
from .models import Lector

@admin.register(Lector)
class LectorAdmin(admin.ModelAdmin):
    list_display = ('codigo_institucional', 'get_nombre_completo', 'tipo', 'estado', 'fecha_registro')
    list_filter = ('tipo', 'estado')
    search_fields = ('codigo_institucional', 'user__first_name', 'user__last_name', 'user__username', 'user__email')

    def get_nombre_completo(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_nombre_completo.short_description = "Nombre Completo"
