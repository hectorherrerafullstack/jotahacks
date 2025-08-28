from django.contrib import admin
from .models import Contacto, Testimonio

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'fecha_envio')
    search_fields = ('nombre', 'email', 'reto')
    list_filter = ('fecha_envio',)

@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'empresa', 'publicado', 'fecha_creacion')
    list_filter = ('publicado',)
    search_fields = ('autor', 'empresa', 'texto')