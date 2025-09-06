from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path('', views.home_view, name='home'),  # Home con hero + 2 CTAs
    path('sobre-mi/', views.acerca_view, name='sobre_mi'),  # Página Sobre mí
    path('contacto/', views.contacto_view, name='contacto'),  # Contacto (form + calendario 15 min)
    path('vinaros-desarrollador-full-stack/', views.vinaros_view, name='vinaros'),  # Página landing Vinaròs
    path('api/chat-gemini/', views.api_chat_gemini, name='api_chat_gemini'),
    
    # Legal (bajo /legal/)
    path('legal/privacidad/', views.privacidad_view, name='privacidad'),  # Política de privacidad
    path('legal/terminos/', views.terminos_view, name='terminos'),        # Términos y condiciones
    path('legal/cookies/', views.cookies_view, name='cookies'),           # Política de cookies
]
