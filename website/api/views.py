"""
Vistas de API para la aplicación de website.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from miweb.security.business_logic import DataProcessor, APISecurityHelper

class ContactProcessor(DataProcessor):
    """
    Procesador seguro para los datos de contacto.
    Mantiene la lógica crítica en el backend.
    """
    
    def validate_data(self, data):
        """Valida los datos de contacto."""
        required_fields = ['name', 'phone', 'message', 'sector']
        
        for field in required_fields:
            if field not in data or not data[field]:
                self.add_error(f"El campo '{field}' es obligatorio.")
                return False
        
        # Validación adicional específica
        if 'phone' in data and not self._validate_phone(data['phone']):
            self.add_error("El formato del teléfono no es válido.")
            return False
        
        return True
    
    def _validate_phone(self, phone):
        """Valida el formato del teléfono."""
        import re
        # Ejemplo simple: al menos 9 dígitos
        return bool(re.match(r'^\+?[\d\s]{9,}$', phone))
    
    def process_data(self, data):
        """Procesa los datos de contacto de forma segura."""
        # Aquí iría la lógica de negocio real, como enviar emails, guardar en BD, etc.
        # Por simplicidad, solo devolvemos los datos procesados
        
        processed_data = {
            'name': data['name'],
            'phone': data['phone'],
            'message': data['message'],
            'sector': data['sector'],
            'status': 'received',
            'priority': self._calculate_priority(data)
        }
        
        return processed_data
    
    def _calculate_priority(self, data):
        """
        Calcula la prioridad del contacto según criterios internos.
        Esta es lógica sensible que debe mantenerse en el backend.
        """
        priority = 'normal'
        
        # Lógica de negocio para determinar la prioridad
        if 'urgent' in data.get('message', '').lower():
            priority = 'high'
        elif data.get('company') and len(data.get('message', '')) > 200:
            priority = 'medium-high'
        elif 'budget' in data and data['budget'] and float(data['budget']) > 10000:
            priority = 'high'
        
        return priority


class ContactAPIView(APIView):
    """
    API para gestionar contactos.
    Utiliza JWT para autenticación y mantiene la lógica crítica en el backend.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Procesa una solicitud de contacto."""
        try:
            # Registrar el acceso a la API
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            APISecurityHelper.log_api_access(
                request.user.id, 
                'contact', 
                'POST', 
                True, 
                client_ip
            )
            
            # Utilizar la clase de lógica de negocio
            processor = ContactProcessor(request)
            result = processor.safe_execute(request.data)
            
            if result['success']:
                return Response(
                    {'status': 'success', 'data': result['result']},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'status': 'error', 'errors': result['errors']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            # Log del error pero sin exponer detalles internos
            import logging
            logging.exception("Error en ContactAPIView")
            
            return Response(
                {'status': 'error', 'message': 'Error al procesar la solicitud'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )