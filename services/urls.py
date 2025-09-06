from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path('', views.index_view, name='servicios_index'),  # Listado/índice de servicios
    path('software-a-medida/', views.software_a_medida_view, name='software_a_medida'),  # Servicio: Software a medida
    path('integraciones-api/', views.integraciones_api_view, name='integraciones_api'),  # Servicio: Integraciones API
    path('automatizacion-procesos-ia/', views.automatizacion_procesos_ia_view, name='automatizacion_procesos_ia'),  # Servicio: Automatización de procesos con IA
    path('erp-crm-medida/', views.erp_crm_medida_view, name='erp_crm_medida'),  # Servicio: ERP/CRM a medida
   
]
