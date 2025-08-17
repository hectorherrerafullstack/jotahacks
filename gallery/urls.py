from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path('', views.proyectos_view, name='proyectos'),  # Listado + filtros de proyectos/casos
    path('<slug:slug>/', views.proyecto_detalle_view, name='proyecto_detalle'),  # Ficha de proyecto por slug
]
