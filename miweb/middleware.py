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
    
    def process_response(self, request, response):
        """
        Procesa la respuesta HTTP para añadir cabeceras de seguridad.
        """
        # Deshabilitar almacenamiento en caché del navegador para evitar
        # que se guarden copias locales fácilmente accesibles
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        # Prevenir que el sitio sea mostrado en frames (clickjacking protection)
        response['X-Frame-Options'] = 'DENY'
        
        # Habilitar protección XSS en navegadores modernos
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Prevenir MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer Policy (controla la información enviada en el header Referer)
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy (limita características del navegador)
        response['Feature-Policy'] = "camera 'none'; microphone 'none'; geolocation 'none'"
        
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
        # La protección JS impide la inspección del código, pero puede afectar funcionalidad legítima
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type and not settings.DEBUG:
            # Inyectar script de protección contra inspección
            if hasattr(response, 'content') and response.content:
                try:
                    content = response.content.decode('utf-8')
                    protection_js = """
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
    
    // Detectar herramientas de desarrollador
    const devtools = {
        isOpen: false,
        orientation: undefined
    };
    
    // Función para detectar apertura de DevTools por cambio de tamaño
    const threshold = 160;
    const emitEvent = function(isOpen, orientation) {
        window.dispatchEvent(new CustomEvent('devtoolschange', {
            detail: {
                isOpen,
                orientation
            }
        }));
    };
    
    // Detección por diferencia de dimensiones
    setInterval(function() {
        const widthThreshold = window.outerWidth - window.innerWidth > threshold;
        const heightThreshold = window.outerHeight - window.innerHeight > threshold;
        const orientation = widthThreshold ? 'vertical' : 'horizontal';
        
        if (
            !(heightThreshold && widthThreshold) &&
            ((window.Firebug && window.Firebug.chrome && window.Firebug.chrome.isInitialized) || widthThreshold || heightThreshold)
        ) {
            if (!devtools.isOpen || devtools.orientation !== orientation) {
                emitEvent(true, orientation);
            }
            devtools.isOpen = true;
            devtools.orientation = orientation;
        } else {
            if (devtools.isOpen) {
                emitEvent(false, undefined);
            }
            devtools.isOpen = false;
            devtools.orientation = undefined;
        }
    }, 500);
    
    // Acción cuando se detectan herramientas de desarrollador
    window.addEventListener('devtoolschange', function(e) {
        if (e.detail.isOpen) {
            // Opcional: redirigir o mostrar un mensaje
            // window.location.href = '/error';
            console.clear();
            console.log('%cAdvertencia!', 'color: red; font-size: 30px; font-weight: bold;');
            console.log('%cEsta es una característica del navegador destinada a desarrolladores. Por favor, cierra esta ventana.', 'font-size: 16px;');
        }
    });
    
    // Deshabilitar debugging con debugger
    setInterval(function() {
        debugger;
    }, 100);
})();
</script>
"""
                    # Insertar antes del cierre del body
                    if '</body>' in content:
                        content = content.replace('</body>', protection_js + '</body>')
                        response.content = content.encode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    # No modificar si no es contenido de texto
                    pass
        
        return response
