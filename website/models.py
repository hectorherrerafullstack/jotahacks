# FILE: website/models.py

from django.db import models

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    web = models.URLField(blank=True, null=True)
    reto = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Contactos"

class Testimonio(models.Model):
    autor = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    publicado = models.BooleanField(default=False)

    def __str__(self):
        return f'Testimonio de {self.autor}'

    class Meta:
        verbose_name_plural = "Testimonios"