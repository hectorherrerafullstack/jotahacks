# Protección del Código de tu Sitio Web

Este documento explica las medidas implementadas para proteger el código de tu sitio web Django y dificultar su inspección por parte de los visitantes.

## Medidas Implementadas

### 1. Middleware de Protección

Se ha creado un middleware personalizado (`SecurityProtectionMiddleware`) que implementa varias protecciones:

- **Cabeceras de seguridad HTTP**: Añade cabeceras que mejoran la seguridad del sitio
- **Protección contra inspección**: Código JavaScript que dificulta el uso de las herramientas de desarrollo
- **Desactivación del clic derecho**: Previene el menú contextual que permite inspeccionar elementos
- **Bloqueo de teclas de desarrollo**: Deshabilita atajos como F12, Ctrl+Shift+I, etc.
- **Detección de herramientas de desarrollo**: Identifica cuando se abren las DevTools

### 2. Cabeceras de Seguridad

Se han configurado cabeceras HTTP que mejoran la seguridad:

- **Content Security Policy (CSP)**: Controla qué recursos puede cargar el navegador
- **X-Frame-Options**: Previene el clickjacking
- **X-XSS-Protection**: Activa la protección contra XSS en navegadores
- **X-Content-Type-Options**: Previene el MIME sniffing
- **Referrer-Policy**: Controla la información del encabezado Referer
- **Feature-Policy**: Limita características como cámara, micrófono, etc.

### 3. Ofuscación de Código JavaScript

Se ha configurado un sistema para ofuscar el código JavaScript:

- **Herramienta de ofuscación**: Utiliza `javascript-obfuscator` para hacer el código difícil de leer
- **Script automatizado**: `obfuscate_js.py` para procesar todos los archivos JS
- **Comandos npm**: Nuevos comandos para construir y ofuscar en un solo paso

## Cómo utilizar estas medidas

### Para activar todas las protecciones:

1. **Ejecuta el proceso de ofuscación antes de desplegar**:
   ```
   python obfuscate_js.py
   ```

2. **Asegúrate de que DEBUG = False en producción**:
   - Todas las protecciones JavaScript se activan solo cuando DEBUG es False
   - Las cabeceras de seguridad más estrictas se aplican en modo producción

3. **Exención de protecciones para ciertas rutas**:
   - Puedes añadir rutas a `CSP_EXEMPT_URLS` en settings.py si necesitas excluir ciertas páginas

## Limitaciones y consideraciones

Es importante entender que estas medidas no son infalibles:

1. **No son 100% efectivas**: Un usuario técnicamente hábil puede superar estas protecciones
2. **Pueden afectar la experiencia de usuario**: Algunas funcionalidades legítimas podrían verse afectadas
3. **El código backend sigue protegido**: Estas medidas se centran en el código frontend (HTML/CSS/JS)

## Recomendaciones adicionales

1. **Mantén el código sensible en el backend**: Nunca coloques secretos o lógica crítica en JavaScript
2. **Utiliza APIs con autenticación**: Para operaciones sensibles, usa APIs con tokens de autenticación
3. **Actualiza regularmente**: Mantén actualizadas estas protecciones ya que los navegadores evolucionan

## Uso en desarrollo

Durante el desarrollo, estas protecciones no estarán activas (cuando DEBUG = True) para facilitar la programación. Se activarán automáticamente en el entorno de producción.