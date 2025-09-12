"""
Configuración de URLs para la API.
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

# URLs para autenticación JWT
urlpatterns = [
    # URLs de autenticación
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # URLs de la API
    path('contact/', views.ContactAPIView.as_view(), name='api_contact'),
]