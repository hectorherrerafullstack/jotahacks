# FILE: miweb/mixins.py

from django.db import models

class SeoMixin(models.Model):
    meta_title = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Título SEO (meta title)"
    )
    meta_description = models.TextField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Descripción SEO (meta description)"
    )
    meta_keywords = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Palabras clave SEO"
    )

    class Meta:
        abstract = True