# miweb/middleware.py
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class BrokenPipeMiddleware:
    """
    Middleware para manejar errores de broken pipe de manera elegante
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Captura excepciones de broken pipe y las maneja silenciosamente
        """
        # Verificar si es un error de broken pipe
        if isinstance(exception, (BrokenPipeError, ConnectionResetError)):
            logger.debug(f"Broken pipe detectado en {request.path} - Cliente desconectado")
            # No hacer nada, el cliente ya se desconectó
            return None
            
        # Para errores relacionados con el chat, devolver respuesta JSON de error
        if '/api/chat/' in request.path and hasattr(exception, '__class__'):
            logger.warning(f"Error en API chat: {exception}")
            return JsonResponse({
                'error': 'Error temporal del servidor. Inténtalo de nuevo.',
                'type': 'server_error'
            }, status=500)
            
        # Para otros errores, dejar que Django los maneje normalmente
        return None
