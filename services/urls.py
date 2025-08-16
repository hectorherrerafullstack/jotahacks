from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path('', views.index_view, name='index'),
    path('automatizacion-datos/', views.automatizacion_datos_view, name='automatizacion_datos'),
    path('ia-para-erp-crm/', views.ia_erp_crm_view, name='ia_erp_crm'),
    path('chatbots-internos/', views.chatbots_internos_view, name='chatbots_internos'),
    path('extraccion-documentos/', views.extraccion_documentos_view, name='extraccion_documentos'),
]