# FILE: demos/models.py

from django.db import models
from django.utils.text import slugify

class AppDemo(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description_corta = models.CharField(max_length=200, verbose_name="Descripción Corta")
    description_larga = models.TextField(verbose_name="Descripción Larga")
    thumbnail_url = models.URLField(verbose_name="URL de Miniatura")
    accepts_files = models.BooleanField(default=False, verbose_name="Acepta archivos")
    accepts_text = models.BooleanField(default=False, verbose_name="Acepta texto")
    
    # Campo para el filtro de categoría
    category = models.CharField(max_length=50, blank=True, verbose_name="Categoría")
    
    # Campo para las etiquetas visibles en la demo
    tags = models.CharField(max_length=200, blank=True, verbose_name="Etiquetas (separadas por coma)")
    
    # Campos dinámicos para el formulario (usado en app_live.html)
    extra_fields = models.JSONField(blank=True, null=True, verbose_name="Campos extra para el formulario")
    
    # Opcionales para la demo
    politica_datos_url = models.URLField(blank=True, verbose_name="URL de política de datos")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(AppDemo, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Demo"
        verbose_name_plural = "Demos"