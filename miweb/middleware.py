"""
Middleware para proteger el código del sitio web y dificultar la inspección en el navegador.
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class SecurityProtectionMiddleware(MiddlewareMixin):
    """
    Middleware que añade cabeceras de seguridad y protecciones adicionales
    para dificultar la inspección del código del sitio.
    """
    
    # Contenido estático del script de protección (cargado una sola vez)
    PROTECTION_JS = """
<script type="text/javascript">
// Protección contra inspección
(function(){
    // Deshabilitar clic derecho
    document.addEventListener('contextmenu', function(e){
        e.preventDefault();
        return false;
    });
    
    // Deshabilitar teclas para inspeccionar elemento
    document.addEventListener('keydown', function(e){
        // F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
        if (
            e.keyCode === 123 || 
            (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74)) ||
            (e.ctrlKey && e.keyCode === 85)
        ) {
            e.preventDefault();
            return false;
        }
    });
    
    // Detectar apertura de herramientas de desarrollador y mostrar mensaje
    window.addEventListener('devtoolschange', function(e) {
        if (e.detail.isOpen) {
            console.clear();
            console.log('%cAdvertencia!', 'color: red; font-size: 30px; font-weight: bold;');
            console.log('%cEsta es una característica del navegador destinada a desarrolladores.', 'font-size: 16px;');
        }
    });
})();
</script>
"""
    
    def process_response(self, request, response):
        """
        Procesa la respuesta HTTP para añadir cabeceras de seguridad.
        """
        # Permitir cacheo estático para mejorar rendimiento
        # Las páginas dinámicas tendrán su propio control de cache
        if 'text/html' in response.get('Content-Type', ''):
            response['Cache-Control'] = 'private, max-age=300'  # 5 minutos para HTML
        else:
            # Para recursos estáticos, permitir cacheo más largo
            response['Cache-Control'] = 'public, max-age=86400'  # 1 día
        
        # Prevenir que el sitio sea mostrado en frames (clickjacking protection)
        response['X-Frame-Options'] = 'DENY'
        
        # Habilitar protección XSS en navegadores modernos
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Prevenir MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer Policy (controla la información enviada en el header Referer)
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Protección básica de Content Security Policy
        # Personalízalo según las necesidades específicas de tu sitio
        if not hasattr(settings, 'CSP_EXEMPT_URLS') or request.path not in settings.CSP_EXEMPT_URLS:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' https://unpkg.com https://fonts.googleapis.com 'unsafe-inline'; "
                "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'; "
                "frame-src 'none'; "
                "object-src 'none'"
            )
        
        # Solo añadir protección JS en páginas HTML y en producción
        # La protección JS simplificada para mejorar rendimiento
        content_type = response.get('Content-Type', '')
        is_html = 'text/html' in content_type
        is_production = not settings.DEBUG
        
        # Verificar si debemos añadir la protección
        if is_html and is_production and hasattr(response, 'content') and response.content:
            try:
                content = response.content.decode('utf-8')
                # Insertar antes del cierre del body
                if '</body>' in content:
                    content = content.replace('</body>', self.PROTECTION_JS + '</body>')
                    response.content = content.encode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                # No modificar si no es contenido de texto
                pass
        
        return response
