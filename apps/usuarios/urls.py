from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('lectores/', views.lector_list, name='lector_list'),
    path('lectores/crear/', views.lector_create, name='lector_create'),
    path('lectores/<int:pk>/editar/', views.lector_update, name='lector_update'),
]
