"""
Middleware de proxy para APIs que oculta los endpoints reales.
"""
import re
import logging
import hashlib
import importlib
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class APIProxyMiddleware(MiddlewareMixin):
    """
    Middleware que actúa como un proxy interno para las API,
    ocultando los endpoints reales y proporcionando una capa
    adicional de seguridad.
    
    NOTA: Este middleware es OPCIONAL y está desactivado por defecto.
    Para activarlo, añade 'ENABLE_API_PROXY = True' en tu settings.py
    """
    
    # URLs que serán procesadas por este middleware
    API_URL_PATTERN = r'^/api/v1/(?P<hash_id>[a-f0-9]{32})/(?P<action>[a-zA-Z0-9_]+)/?$'
    
    # Mapeo de hash a endpoints reales (en producción se almacenaría en la base de datos)
    # En este ejemplo simplificado, lo definimos como una constante
    API_ENDPOINTS = {
        # El hash se genera a partir del endpoint real
        'ea8e8d1aea74c3d4a47e16449bd8c221': {
            'module': 'website.api.views',
            'class': 'ContactAPIView',
            'methods': ['POST'],
        },
        '7b23e49f8e3fabc5697fecb0b8e8e8e7': {
            'module': 'services.api.views',
            'class': 'ServiceListAPIView',
            'methods': ['GET'],
        },
        # Añadir más endpoints según sea necesario
    }
    
    @staticmethod
    def generate_endpoint_hash(endpoint_path):
        """Genera un hash para un endpoint específico."""
        # Usar una sal secreta para hacer más difícil el reverse engineering
        salt = getattr(settings, 'API_HASH_SALT', settings.SECRET_KEY)
        hash_input = f"{endpoint_path}:{salt}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def process_request(self, request):
        """
        Procesa la solicitud entrante, verificando si es una llamada a la API
        y redireccionándola al endpoint real si corresponde.
        """
        # Verificar si el proxy está habilitado en la configuración
        if not getattr(settings, 'ENABLE_API_PROXY', False):
            # El proxy está desactivado, no procesar la solicitud
            return None
            
        # Solo procesar solicitudes que coincidan con el patrón de URL de la API
        path = request.path_info
        match = re.match(self.API_URL_PATTERN, path)
        
        if not match:
            # No es una solicitud de API, continuar con el procesamiento normal
            return None
        
        hash_id = match.group('hash_id')
        action = match.group('action')
        
        # Verificar si el hash existe en nuestro mapeo
        if hash_id not in self.API_ENDPOINTS:
            logger.warning(f"Intento de acceso a endpoint de API desconocido: {hash_id}")
            return JsonResponse({'error': 'Endpoint no encontrado'}, status=404)
        
        endpoint_info = self.API_ENDPOINTS[hash_id]
        
        # Verificar si el método HTTP está permitido
        if request.method not in endpoint_info['methods']:
            logger.warning(f"Método no permitido {request.method} para endpoint {hash_id}")
            return JsonResponse(
                {'error': f"Método {request.method} no permitido"},
                status=405
            )
        
        try:
            # Importar dinámicamente la vista
            module = importlib.import_module(endpoint_info['module'])
            view_class = getattr(module, endpoint_info['class'])
            
            # Crear una instancia de la vista
            view_instance = view_class()
            
            # Llamar al método correspondiente (dispatch para vistas basadas en clase)
            # o directamente al método si es una función
            if hasattr(view_instance, 'dispatch'):
                view_instance.request = request
                view_instance.args = []
                view_instance.kwargs = {'action': action}
                response = view_instance.dispatch(request, action=action)
            else:
                response = view_instance(request, action=action)
            
            return response
        
        except ImportError:
            logger.exception(f"Error al importar el módulo {endpoint_info['module']}")
            return JsonResponse(
                {'error': 'Error interno del servidor'},
                status=500
            )
        except AttributeError:
            logger.exception(f"Clase o método no encontrado: {endpoint_info['class']}")
            return JsonResponse(
                {'error': 'Error interno del servidor'},
                status=500
            )
        except Exception as e:
            logger.exception(f"Error al procesar la solicitud: {str(e)}")
            return JsonResponse(
                {'error': 'Error interno del servidor'},
                status=500
            )