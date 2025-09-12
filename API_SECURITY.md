# Seguridad Avanzada de API y Protección de Lógica de Negocio

Este documento describe las medidas avanzadas de seguridad implementadas para proteger la lógica de negocio sensible y asegurar las API de la aplicación.

> **IMPORTANTE**: Todas estas características son **OPCIONALES** y están **DESACTIVADAS por defecto**. 
> Tu aplicación seguirá funcionando exactamente igual que antes sin ninguna modificación.
> Consulta [KOYEB_CONFIG.md](./KOYEB_CONFIG.md) para instrucciones sobre cómo activarlas de forma segura.

## 1. Protección de Lógica de Negocio en el Backend

Se ha implementado un sistema para mantener toda la lógica sensible del negocio en el backend, impidiendo su exposición en el código JavaScript del frontend.

### Estructura Implementada

- **Módulo `miweb.security.business_logic`**: Proporciona clases base para encapsular lógica sensible
- **Clase `SecureBusinessLogic`**: Clase abstracta para implementar lógica protegida
- **Clase `DataProcessor`**: Para procesar datos de forma segura
- **Ejemplo: `ContactProcessor`**: Implementación específica para procesar datos de contacto

### Beneficios de Esta Aproximación

- La lógica crítica del negocio nunca llega al navegador
- Las validaciones se realizan en el servidor
- Los algoritmos sensibles permanecen ocultos
- Centralización de la lógica para facilitar auditorías y actualizaciones

## 2. API con Autenticación JWT

Se ha implementado un sistema de autenticación basado en JSON Web Tokens (JWT) para todas las APIs.

### Características Implementadas

- **Tokens de Acceso y Refresco**: Sistema completo de autenticación
- **Permisos Basados en Roles**: Control granular de acceso
- **Configuración Segura**: Tiempos de expiración, algoritmos seguros, etc.
- **Integración con Django REST Framework**: Para facilitar el desarrollo

### Flujo de Autenticación

1. El cliente se autentica con credenciales y recibe un token JWT
2. Las solicitudes posteriores incluyen el token en el encabezado
3. El servidor valida el token antes de procesar cada solicitud
4. Los tokens expiran automáticamente por seguridad

## 3. Proxy de API para Ocultar Endpoints Reales

Se ha implementado un middleware que actúa como proxy para ocultar los endpoints reales de la API.

### Funcionamiento

- **Hashing de Rutas**: Los endpoints reales se ocultan tras hashes
- **URL Pública**: `/api/v1/{hash_id}/{action}/`
- **Enrutamiento Dinámico**: El middleware redirecciona internamente a la vista correcta
- **Validación de Método**: Comprueba que el método HTTP sea permitido

### Ventajas de Seguridad

- Dificulta el descubrimiento de endpoints
- Añade una capa adicional de protección
- Previene ataques automatizados y escaneos
- Facilita la auditoría centralizada de accesos

## 4. Implementación Técnica

### Archivos Creados/Modificados

- `miweb/security/business_logic.py`: Clases para encapsular lógica de negocio
- `miweb/security/api_proxy.py`: Middleware de proxy para APIs
- `website/api/views.py`: Implementación de ejemplo de API segura
- `miweb/settings.py`: Configuración de seguridad y JWT
- `website/api/urls.py`: Configuración de rutas de autenticación

### Configuración en Django Settings

```python
# REST Framework con JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Configuración JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # Otras configuraciones...
}
```

## 5. Uso y Desarrollo

### Activación de las características

Para activar estas características, debes configurar las siguientes variables de entorno:

```
ENABLE_API_PROXY=True   # Activa el proxy de API
ENABLE_JWT_AUTH=True    # Activa la autenticación JWT
```

Por defecto, todas las características están desactivadas para mantener la compatibilidad con sistemas existentes.

### Para desarrolladores: Creación de nuevos endpoints seguros

1. Crea una clase derivada de `SecureBusinessLogic` para tu lógica de negocio
2. Implementa la vista de API usando Django REST Framework
3. Genera un hash para el endpoint y añádelo al diccionario `API_ENDPOINTS`
4. Accede al endpoint a través del proxy: `/api/v1/{hash_id}/{action}/`

### Obtención de tokens JWT

```python
import requests

# Obtener token
response = requests.post(
    'https://tudominio.com/api/auth/token/',
    data={'username': 'usuario', 'password': 'contraseña'}
)
token = response.json()['access']

# Usar el token
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'https://tudominio.com/api/v1/{hash_id}/action/',
    headers=headers,
    json=data
)
```

## 6. Consideraciones de Seguridad Adicionales

- Actualiza regularmente la librería JWT para parchar vulnerabilidades
- Rota las claves de firma JWT periódicamente
- Configura HTTPS para todas las comunicaciones
- Implementa rate limiting para prevenir ataques de fuerza bruta
- Monitoriza los logs de acceso para detectar patrones sospechosos

## 7. Compatibilidad con Despliegues Existentes

Estas características han sido diseñadas para ser completamente compatibles con despliegues existentes:

- **Activación Progresiva**: Cada característica puede activarse independientemente
- **Sin Cambios en Rutas Existentes**: Las URLs actuales siguen funcionando igual
- **Fácil Rollback**: Si hay problemas, simplemente desactiva las características

Consulta [KOYEB_CONFIG.md](./KOYEB_CONFIG.md) para instrucciones detalladas sobre cómo configurar tu despliegue en Koyeb.

## 8. Pruebas de Seguridad Recomendadas

- Pruebas de penetración centradas en la API
- Análisis de tokens JWT para verificar configuración
- Intentos de reverse engineering del proxy
- Verificación de que la lógica sensible no se filtra al frontend