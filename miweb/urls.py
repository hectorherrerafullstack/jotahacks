from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Panel de administración de Django

    # Sitio público (home, acerca, contacto, legal...). Namespace: website
    path('', include(('website.urls', 'website'), namespace='website')),

    # Sección de Servicios (listado + 4 servicios). Namespace: services
    path('servicios/', include(('services.urls', 'services'), namespace='services')),

    # Portafolio / Casos (listado + detalle). Namespace: gallery
    path('proyectos/', include(('gallery.urls', 'gallery'), namespace='gallery')),

    # Mini-apps/demos (índice + app en vivo). Namespace: demos
    path('apps/', include(('demos.urls', 'demos'), namespace='demos')),

    # Blog (índice + post). Namespace: blog
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
]

# Archivos subidos (solo en DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
