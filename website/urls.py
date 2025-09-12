# project/apps/website/urls.py
from django.urls import path
from .views import (
    api_chat_gemini,
    home_view, acerca_view, contacto_view,
    privacidad_view, terminos_view, cookies_view,
    vinaros_view, castellon_view,
)

app_name = "website"

urlpatterns = [
    path("", home_view, name="home"),
    path("sobre-mi/", acerca_view, name="acerca"),
    path("contacto/", contacto_view, name="contacto"),
    path("legal/privacidad/", privacidad_view, name="privacidad"),
    path("legal/terminos/", terminos_view, name="terminos"),
    path("legal/cookies/", cookies_view, name="cookies"),
    path("vinaros/", vinaros_view, name="vinaros"),
    path("castellon/", castellon_view, name="castellon"),
    path("api/chat-gemini/", api_chat_gemini, name="api_chat_gemini"),
]
