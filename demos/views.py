from django.shortcuts import render

def apps_index_view(request):
    return render(request, 'demos/apps_index.html')

def app_live_view(request, slug):
    return render(request, 'demos/app_live.html', {'slug': slug})
