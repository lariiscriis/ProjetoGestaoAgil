from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponse

from .forms import CadastroForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario

def app(request):
    return render(request, 'landing-page.html')

def linkAjuda(request):
    return render(request, 'ajuda.html')



# def cadastro(request):
#     userForm = CadastroForm(request.POST or None)
    
#     if request.method == 'POST':
#         if userForm.is_valid():
#             emailForm = userForm.cleaned_data.get('email')
            
#             if Usuario.objects.filter(email=emailForm).exists():
#                 userForm.add_error('email', 'Email já cadastrado.')
#             else:
#                 usuario = userForm.save(commit=False)
#                 usuario.senha = make_password(usuario.senha) 
#                 usuario.save()
#                 return redirect("exibirUsuarios")
    
#     return render(request, 'login_cadastro_base.html', {'form': userForm, 'action': 'login'})

def login_view(request):
    error = None
    action = request.GET.get('action', 'login') 
    if action == 'login':
        # Formulário de Login
        loginForm = LoginForm(request.POST or None)

        if request.method == 'POST' and loginForm.is_valid():
            email = loginForm.cleaned_data['email']
            senha = loginForm.cleaned_data['senha']

            try:
                usuario = Usuario.objects.get(email=email)

                if check_password(senha, usuario.senha):
                    request.session['usuario_id'] = usuario.id
                    return redirect('exibirUsuarios')
                else:
                    error = 'Senha incorreta.'
            except Usuario.DoesNotExist:
                error = 'Usuário não encontrado.'

        return render(request, 'login_cadastro_base.html', {'form': loginForm, 'error': error, 'action': 'login'})
    
    elif action == 'cadastro':
        # Formulário de Cadastro
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
                    return redirect('exibirUsuarios')

        return render(request, 'login_cadastro_base.html', {'form': userForm, 'error': error,'action': 'cadastro'})


def exibirUsuarios(request):
    usuarios = Usuario.objects.all().values()
    return render(request, "usuarios.html", {'listUsuarios': usuarios})