from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include(('website.urls', 'website'), namespace='website')),
    path('servicios/', include(('services.urls', 'services'), namespace='services')),
    path('proyectos/', include(('gallery.urls', 'gallery'), namespace='gallery')),
    path('apps/', include(('demos.urls', 'demos'), namespace='demos')),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
