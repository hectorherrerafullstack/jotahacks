from django.shortcuts import render

def index_view(request):
    return render(request, 'services/index.html')

def automatizacion_datos_view(request):
    return render(request, 'services/automatizacion_datos.html')

def ia_erp_crm_view(request):
    return render(request, 'services/ia_erp_crm.html')

def chatbots_internos_view(request):
    return render(request, 'services/chatbots_internos.html')

def extraccion_documentos_view(request):
    return render(request, 'services/extraccion_documentos.html')
