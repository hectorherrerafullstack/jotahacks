from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path('', views.index_view, name='servicios_index'),  # Listado/índice de servicios
    path('automatizacion-datos/', views.automatizacion_datos_view, name='automatizacion_datos'),  # Servicio: Automatización de datos
    path('ia-para-erp-crm/', views.ia_erp_crm_view, name='ia_erp_crm'),  # Servicio: IA para ERP/CRM
    path('chatbots-internos/', views.chatbots_internos_view, name='chatbots_internos'),  # Servicio: Chatbots internos
    path('extraccion-documentos/', views.extraccion_documentos_view, name='extraccion_documentos'),  # Servicio: Extracción documental
]
