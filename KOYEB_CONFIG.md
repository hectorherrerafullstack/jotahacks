# Configuración de Variables de Entorno para Koyeb

Esta guía explica cómo configurar las variables de entorno en Koyeb para utilizar las nuevas características de seguridad sin afectar tu despliegue existente.

## Variables de Entorno para Características de Seguridad

Todas las nuevas características de seguridad están **desactivadas por defecto**, lo que significa que tu aplicación seguirá funcionando exactamente igual que antes, sin ninguna modificación.

Para activar las características de forma progresiva, puedes añadir estas variables de entorno en el panel de control de Koyeb:

### Variables Principales:

| Variable | Valor Recomendado | Descripción |
|----------|-------------------|-------------|
| `ENABLE_API_PROXY` | `False` | Activa el proxy de API que oculta los endpoints reales |
| `ENABLE_JWT_AUTH` | `False` | Activa la autenticación JWT para las APIs |

### Proceso de Activación Recomendado:

1. **Primera fase (actual)**: Mantén todas las características desactivadas para asegurar que todo funciona correctamente.
2. **Segunda fase**: Activa primero `ENABLE_JWT_AUTH` y prueba que la autenticación funciona correctamente.
3. **Tercera fase**: Activa `ENABLE_API_PROXY` una vez que hayas adaptado el frontend para utilizar las nuevas rutas.

## Instrucciones para Configuración en Koyeb

1. Accede al dashboard de Koyeb
2. Selecciona tu aplicación
3. Ve a la pestaña "Environment"
4. Añade las variables con los valores deseados
5. Guarda los cambios y espera a que se complete el despliegue

## Compatibilidad con el Despliegue Existente

Las modificaciones se han diseñado para ser totalmente compatibles con tu despliegue existente:

- El sistema sigue funcionando exactamente igual si las características están desactivadas
- No hay cambios en las rutas existentes
- Las clases de lógica de negocio son independientes y no afectan al código actual

## Cómo Probar en Producción de Forma Segura

Para probar las nuevas características en producción sin afectar a los usuarios:

1. Mantén `ENABLE_API_PROXY` y `ENABLE_JWT_AUTH` como `False`
2. Usa las clases de lógica de negocio en tus vistas existentes (esto no romperá nada)
3. Cuando estés listo, activa las características una por una monitorizando los logs

## Rollback en Caso de Problemas

Si experimentas algún problema, simplemente:

1. Establece todas las variables en `False`
2. Redespliega la aplicación

Esto desactivará todas las nuevas características y volverá al comportamiento anterior inmediatamente.