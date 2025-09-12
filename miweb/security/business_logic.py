"""
Módulo de utilidades para mantener la lógica sensible en el backend.
Este módulo proporciona clases base y funciones para encapsular la lógica
de negocio crítica, evitando su exposición en el frontend.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpRequest

logger = logging.getLogger(__name__)

class SecureBusinessLogic(ABC):
    """
    Clase base abstracta para encapsular lógica de negocio sensible.
    Esta clase proporciona métodos seguros para procesar datos
    sin exponer los detalles de la implementación al frontend.
    """
    
    def __init__(self, request: Optional[HttpRequest] = None):
        """Inicializa la clase con la solicitud HTTP opcional."""
        self.request = request
        self._errors = []
        self._result = None
    
    @property
    def errors(self) -> List[str]:
        """Devuelve los errores acumulados durante el procesamiento."""
        return self._errors
    
    @property
    def result(self) -> Any:
        """Devuelve el resultado del procesamiento."""
        return self._result
    
    def add_error(self, error: str) -> None:
        """Añade un error a la lista de errores."""
        self._errors.append(error)
    
    def has_errors(self) -> bool:
        """Comprueba si hay errores."""
        return len(self._errors) > 0
    
    def clear(self) -> None:
        """Limpia los errores y el resultado."""
        self._errors = []
        self._result = None
    
    @abstractmethod
    def process(self, *args, **kwargs) -> bool:
        """
        Método abstracto que debe ser implementado por las subclases.
        Debe procesar la lógica de negocio y devolver True si el procesamiento
        fue exitoso, False en caso contrario.
        """
        pass
    
    def safe_execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta el procesamiento de forma segura, capturando excepciones.
        Devuelve un diccionario con el resultado y los errores.
        """
        try:
            success = self.process(*args, **kwargs)
            return {
                'success': success,
                'result': self.result if success else None,
                'errors': self.errors if not success else []
            }
        except ValidationError as e:
            self.add_error(str(e))
            logger.warning(f"Validation error in {self.__class__.__name__}: {e}")
            return {
                'success': False,
                'result': None,
                'errors': self.errors
            }
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.add_error(error_msg)
            logger.exception(f"Unexpected error in {self.__class__.__name__}")
            return {
                'success': False,
                'result': None,
                'errors': self.errors
            }


class DataProcessor(SecureBusinessLogic):
    """
    Clase para procesar datos de forma segura.
    Implementa la lógica genérica para procesar datos y validarlos.
    """
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida los datos de entrada.
        Debe ser implementado por las subclases si es necesario.
        """
        return True
    
    def process_data(self, data: Dict[str, Any]) -> Any:
        """
        Procesa los datos validados.
        Debe ser implementado por las subclases.
        """
        return data
    
    def process(self, data: Dict[str, Any]) -> bool:
        """
        Implementación del método abstracto process.
        Valida y procesa los datos, estableciendo el resultado.
        """
        if not self.validate_data(data):
            return False
        
        try:
            self._result = self.process_data(data)
            return True
        except Exception as e:
            self.add_error(f"Error al procesar datos: {str(e)}")
            return False


class APISecurityHelper:
    """
    Clase de utilidad para añadir seguridad a las API.
    Proporciona métodos para validar tokens, verificar permisos, etc.
    """
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Valida un token de autenticación.
        En una implementación real, esto verificaría la validez del token JWT.
        """
        # Aquí iría la lógica real de validación del token
        return len(token) > 10
    
    @staticmethod
    def check_permissions(user_id: int, resource: str, action: str) -> bool:
        """
        Verifica si un usuario tiene permisos para realizar una acción
        sobre un recurso específico.
        """
        # Aquí iría la lógica real de verificación de permisos
        return True
    
    @staticmethod
    def log_api_access(user_id: Optional[int], endpoint: str, method: str, 
                      success: bool, ip_address: str) -> None:
        """
        Registra el acceso a una API para auditoría de seguridad.
        """
        import datetime
        log_entry = {
            'user_id': user_id,
            'endpoint': endpoint,
            'method': method,
            'success': success,
            'ip_address': ip_address,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        logger.info(f"API Access: {json.dumps(log_entry)}")