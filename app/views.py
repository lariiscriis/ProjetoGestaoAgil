from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

def app(request):
    return render(request, 'landing-page.html')

def linkAjuda(request):
    return render(request, 'ajuda.html')