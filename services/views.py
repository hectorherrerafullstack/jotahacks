from django.shortcuts import render

def index_view(request):
    return render(request, 'servicios/index.html')

def software_a_medida_view(request):
    return render(request, 'servicios/software-a-medida.html')

def integraciones_api_view(request):
    return render(request, 'servicios/integraciones-api.html')

def automatizacion_procesos_ia_view(request):
    return render(request, 'servicios/automatizacion-procesos-ia.html')

def erp_crm_medida_view(request):
    return render(request, 'servicios/erp-crm-medida.html')



