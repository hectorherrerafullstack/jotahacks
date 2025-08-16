from django.shortcuts import render

def home_view(request):
    return render(request, 'website/home.html')

def acerca_view(request):
    return render(request, 'website/acerca.html')

def contacto_view(request):
    return render(request, 'website/contacto.html')

def privacidad_view(request):
    return render(request, 'website/legal/privacidad.html')

def terminos_view(request):
    return render(request, 'website/legal/terminos.html')

def cookies_view(request):
    return render(request, 'website/legal/cookies.html')
