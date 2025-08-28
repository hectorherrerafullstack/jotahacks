# FILE: blog/models.py

from django.db import models
from django.utils.text import slugify

# Se asume que has creado miweb/mixins.py
# y que contiene el SeoMixin
from miweb.mixins import SeoMixin

class Post(SeoMixin, models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.CharField(max_length=250, verbose_name="Extracto")
    content = models.TextField(verbose_name="Contenido")
    published_at = models.DateTimeField(verbose_name="Fecha de Publicación")
    cover_url = models.URLField(verbose_name="URL de Portada")
    author_name = models.CharField(max_length=100, default='Equipo', verbose_name="Autor")
    read_time = models.IntegerField(verbose_name="Tiempo de lectura (min)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ['-published_at']