from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', 'hero_heading')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('demos_relacionadas',)