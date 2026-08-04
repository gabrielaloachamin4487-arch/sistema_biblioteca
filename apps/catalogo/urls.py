from django.urls import path
from . import views

urlpatterns = [
    path('', views.libro_list, name='libro_list'),
    path('<int:pk>/', views.libro_detail, name='libro_detail'),
    path('crear/', views.libro_create, name='libro_create'),
    path('<int:pk>/editar/', views.libro_update, name='libro_update'),
    path('<int:pk>/eliminar/', views.libro_delete, name='libro_delete'),
]
