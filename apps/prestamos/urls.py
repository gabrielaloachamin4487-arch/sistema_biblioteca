from django.urls import path
from . import views

urlpatterns = [
    path('', views.prestamo_list, name='prestamo_list'),
    path('crear/', views.prestamo_create, name='prestamo_create'),
    path('<int:pk>/devolucion/', views.prestamo_devolucion, name='prestamo_devolucion'),
    path('<int:pk>/enviar-correo/', views.enviar_correo_directo, name='enviar_correo_directo'),
    path('morosos/', views.morosos_list, name='morosos_list'),
    path('exportar/inventario/', views.exportar_inventario, name='exportar_inventario'),
    path('exportar/morosos/excel/', views.exportar_morosos_excel_view, name='exportar_morosos_excel'),
    path('exportar/morosos/csv/', views.exportar_morosos_csv_view, name='exportar_morosos_csv'),
]
