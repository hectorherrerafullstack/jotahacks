# website/urls.py
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path('', views.home_view, name='home'),
    path('acerca/', views.acerca_view, name='acerca'),
    path('contacto/', views.contacto_view, name='contacto'),
    path('legal/privacidad/', views.privacidad_view, name='privacidad'),
    path('legal/terminos/', views.terminos_view, name='terminos'),
    path('legal/cookies/', views.cookies_view, name='cookies'),
]
