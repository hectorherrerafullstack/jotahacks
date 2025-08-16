from django.shortcuts import render

def proyectos_view(request):
    return render(request, 'gallery/proyectos.html')

def proyecto_detalle_view(request, slug):
    return render(request, 'gallery/proyecto_detalle.html', {'slug': slug})
