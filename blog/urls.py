from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path('', views.blog_index_view, name='blog_index'),  # Listado de posts
    path('<slug:slug>/', views.post_view, name='post'),  # Post individual por slug
]
