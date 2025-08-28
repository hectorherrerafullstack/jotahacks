from django.contrib import admin
from .models import Proyecto

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_publicacion', 'demo_slug')
    list_filter = ('fecha_publicacion',)
    search_fields = ('titulo', 'resumen', 'reto', 'enfoque')
    prepopulated_fields = {'slug': ('titulo',)}