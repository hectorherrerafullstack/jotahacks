# FILE: gallery/models.py

from django.db import models
from django.utils.text import slugify

# Se asume que has creado miweb/mixins.py con el SeoMixin
from miweb.mixins import SeoMixin

class Proyecto(SeoMixin, models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título del Proyecto")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    resumen = models.CharField(max_length=250, verbose_name="Resumen")
    cover_url = models.URLField(verbose_name="URL de Portada")
    fecha_publicacion = models.DateField(verbose_name="Fecha de Publicación")
    
    # Campos para la página de detalle
    reto = models.TextField(verbose_name="Reto")
    enfoque = models.TextField(verbose_name="Enfoque")
    kpis = models.JSONField(blank=True, null=True, verbose_name="Resultados (KPIs)")
    stack = models.CharField(max_length=250, verbose_name="Stack Tecnológico")
    video_url = models.URLField(blank=True, null=True, verbose_name="URL de Video")
    demo_slug = models.SlugField(max_length=100, blank=True, null=True, verbose_name="Slug de demo relacionada")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super(Proyecto, self).save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"