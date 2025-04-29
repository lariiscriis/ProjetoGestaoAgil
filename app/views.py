from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponse

from .forms import CadastroForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario

def app(request):
    return render(request, 'landing-page.html')

def linkAjuda(request):
    return render(request, 'ajuda.html')

def cadastro(request):
    userForm = CadastroForm(request.POST or None)
    if request.method == 'POST':
        if userForm.is_valid():
            emailForm = userForm.cleaned_data.get('email')
            if Usuario.objects.filter(email=emailForm).exists():
                userForm.add_error('email', 'Email já cadastrado.')
            else:
                usuario = userForm.save(commit=False)
                usuario.senha = make_password(usuario.senha)
                usuario.save()
                return redirect("exibirUsuarios")
    return render(request, 'cadastro.html', {'form': userForm})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['senha']
        usuario = Usuario.objects.get(email=email)
        if check_password(senha, usuario.senha):
            request.session['usuario_id'] = usuario.id
            return redirect('exibirUsuarios')

    return render(request, 'login.html')


def exibirUsuarios(request):
    usuarios = Usuario.objects.all().values()
    return render(request, "usuarios.html", {'listUsuarios': usuarios})