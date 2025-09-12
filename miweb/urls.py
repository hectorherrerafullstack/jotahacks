from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from services.views import software_a_medida_view, integraciones_api_view, automatizacion_procesos_ia_view, erp_crm_medida_view

urlpatterns = [
    path('admin/', admin.site.urls),  # Panel de administración de Django

    # Sitio público (home, acerca, contacto, legal...). Namespace: website
    path('', include(('website.urls', 'website'), namespace='website')),

    # API endpoints seguros
    path('api/auth/', include('website.api.urls')),  # Endpoints de autenticación

    # Rutas directas para servicios (sin prefijo servicios)
    path('software-a-medida/', software_a_medida_view, name='software_a_medida_direct'),
    path('integraciones-api/', integraciones_api_view, name='integraciones_api_direct'),
    path('automatizacion-procesos-ia/', automatizacion_procesos_ia_view, name='automatizacion_procesos_ia_direct'),
    path('erp-crm-medida/', erp_crm_medida_view, name='erp_crm_medida_direct'),

    # Sección de Servicios (listado + 4 servicios). Namespace: services
    path('servicios/', include(('services.urls', 'services'), namespace='services')),
    
    # Portafolio / Casos (listado + detalle). Namespace: gallery
    # path('proyectos/', include(('gallery.urls', 'gallery'), namespace='gallery')),

    # Mini-apps/demos (índice + app en vivo). Namespace: demos
    path('apps/', include(('demos.urls', 'demos'), namespace='demos')),

    # Blog (índice + post). Namespace: blog
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
]

# Archivos subidos (solo en DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
