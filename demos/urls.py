from django.urls import path
from . import views

app_name = "demos"

urlpatterns = [
    path('', views.apps_index_view, name='apps_index'),
    path('<slug:slug>/', views.app_live_view, name='app_live'),
]
