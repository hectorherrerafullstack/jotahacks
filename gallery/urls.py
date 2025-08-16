from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path('', views.proyectos_view, name='proyectos'),
    path('<slug:slug>/', views.proyecto_detalle_view, name='proyecto_detalle'),
]
