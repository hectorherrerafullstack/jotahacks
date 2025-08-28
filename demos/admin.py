from django.contrib import admin
from .models import AppDemo

@admin.register(AppDemo)
class AppDemoAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'accepts_files', 'accepts_text')
    list_filter = ('category', 'accepts_files', 'accepts_text')
    search_fields = ('name', 'description_corta', 'tags')
    prepopulated_fields = {'slug': ('name',)}