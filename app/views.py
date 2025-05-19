from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponse

from .forms import CadastroForm, LoginForm, CadastroPsicologoForm
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
    action = request.GET.get('action', 'login')
    tipo = request.POST.get('tipo') or request.GET.get('tipo', 'usuario')

    if action == 'login':
        form = LoginForm(request.POST or None)
        error = None

        if request.method == 'POST':
            print("Dados POST:", request.POST)

            if form.is_valid():
                print("Formulário válido:", form.cleaned_data)
                email = form.cleaned_data.get('email')
                senha = form.cleaned_data.get('senha')

                try:
                    if tipo == 'psicologo':
                        crp = form.cleaned_data.get('crp')
                        if not crp:
                            error = 'CRP é obrigatório para psicólogos.'
                        else:
                            usuario = Usuario.objects.get(email=email, crp=crp, tipo='psicologo')
                    else:
                        usuario = Usuario.objects.get(email=email, tipo='usuario')

                    if check_password(senha, usuario.senha):
                        request.session['usuario_id'] = usuario.id
                        return redirect('exibirUsuarios')
                    else:
                        error = 'Senha inválida.'

                except Usuario.DoesNotExist:
                    error = 'Usuário não encontrado.'

            else:
                print("Formulário inválido:", form.errors)

        return render(request, 'login_cadastro_base.html', {
            'form': form,
            'action': 'login',
            'tipo': tipo,
            'error': error,
        })


    elif action == 'cadastro':
        if tipo == 'psicologo':
            cadastro_form = CadastroPsicologoForm(request.POST or None)
        else:
            cadastro_form = CadastroForm(request.POST or None)

        if request.method == 'POST' and cadastro_form.is_valid():
            email = cadastro_form.cleaned_data.get('email')
            if Usuario.objects.filter(email=email).exists():
                cadastro_form.add_error('email', 'Email já cadastrado.')
            else:
                cadastro_form.save()
                return redirect('exibirUsuarios')

        return render(request, 'login_cadastro_base.html', {
            'form': cadastro_form,
            'action': 'cadastro',
            'tipo': tipo
        })



def exibirUsuarios(request):
    usuarios = Usuario.objects.all().values()
    return render(request, "usuarios.html", {'listUsuarios': usuarios})