# FILE: services/models.py

from django.db import models
from django.utils.text import slugify
from miweb.mixins import SeoMixin

# Importa el modelo AppDemo desde la aplicación 'demos'
from demos.models import AppDemo

class Service(SeoMixin, models.Model):
    title = models.CharField(max_length=200, verbose_name="Título del Servicio")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    hero_heading = models.CharField(max_length=250, verbose_name="Título del Hero")
    hero_subheading = models.TextField(verbose_name="Subtítulo del Hero")
    
    # Secciones de contenido
    problema = models.TextField(verbose_name="Sección: El problema")
    solucion = models.TextField(verbose_name="Sección: Nuestra solución")
    beneficios = models.JSONField(verbose_name="Sección: Beneficios")
    como_trabajo = models.JSONField(verbose_name="Sección: Cómo trabajo (pasos)")
    faq = models.JSONField(verbose_name="Sección: Preguntas frecuentes")
    
    # Relación con las demos
    demos_relacionadas = models.ManyToManyField(
        AppDemo, 
        blank=True, 
        verbose_name="Demos relacionadas"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"