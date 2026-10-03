from django.shortcuts import render

def fruit_recognition_view(request):
    return render(request, 'index.html')