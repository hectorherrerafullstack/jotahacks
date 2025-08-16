from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def blog_index_view(request):
    return render(request, 'blog/index.html')

def post_view(request, slug):
    return render(request, 'blog/post.html', {'slug': slug})
