from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path('', views.home_view, name='home'),  # Home con hero + 2 CTAs
    path('acerca/', views.acerca_view, name='acerca'),  # Página Acerca
    path('contacto/', views.contacto_view, name='contacto'),  # Contacto (form + calendario 15 min)

    # Legal (bajo /legal/)
    path('legal/privacidad/', views.privacidad_view, name='privacidad'),  # Política de privacidad
    path('legal/terminos/', views.terminos_view, name='terminos'),        # Términos y condiciones
    path('legal/cookies/', views.cookies_view, name='cookies'),           # Política de cookies
]
