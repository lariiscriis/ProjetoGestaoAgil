from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from .forms import CadastroForm, LoginForm, CadastroPsicologoForm, PostForm, ComentarioForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Post, Comentario, Curtida
from bson import ObjectId 

def app(request):
    return render(request, 'landing-page.html')

def linkAjuda(request):
    return render(request, 'ajuda.html')

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
                            try:
                                usuario = Usuario.objects.get(email=email, crp=crp, tipo='psicologo')
                            except Usuario.DoesNotExist:
                                usuario = None
                    else:
                        try:
                            usuario = Usuario.objects.get(email=email, tipo='usuario')
                        except Usuario.DoesNotExist:
                            usuario = None

                    if usuario and check_password(senha, usuario.senha):
                        request.session['usuario_id'] = str(usuario._id)
                        print("ID salvo na sessão:", request.session['usuario_id'])
                        return redirect('blog')
                    else:
                        error = 'Email, CRP ou senha inválidos.'


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

# # Blog Views 
def blog(request):
    posts = Post.objects.all()
    usuario = None
    usuario_id = request.session.get('usuario_id')

    if usuario_id:
        try:
            usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        except Usuario.DoesNotExist:
            pass

    return render(request, 'blog.html', {'posts': posts, 'usuario': usuario})


def detalhe_post(request, post_id):
    post = get_object_or_404(Post, _id=ObjectId(post_id))
    comentarios = Comentario.objects.filter(post_id=post, comentario_pai=None).order_by('-data_criacao')

    form = ComentarioForm()
    usuario_id = request.session.get('usuario_id')
    
    if request.method == 'POST' and usuario_id:
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post_id = post
            comentario.autor = Usuario.objects.get(_id=ObjectId(usuario_id))
            
            comentario_pai_id = request.POST.get('comentario_pai_id')
            if comentario_pai_id:
                comentario.comentario_pai = Comentario.objects.get(_id=ObjectId(comentario_pai_id))
            
            comentario.save()
            return redirect('detalhe_post', post_id=post_id)
        
    posts_do_autor = Post.objects.filter(autor=post.autor).exclude(_id=post._id)[:5]  

    return render(request, 'detalhe_post.html', {
        'post': post,
        'comentarios': comentarios,
        'form': form,
        'usuario_id': usuario_id,
        'posts_do_autor': posts_do_autor,
    })

def curtir_post(request, post_id):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        post = Post.objects.get(_id=ObjectId(post_id))

        if not Curtida.objects.filter(usuario=usuario, post_id=post).exists():
            Curtida.objects.create(usuario=usuario, post_id=post, comentario_id=None)
    return redirect('detalhe_post', post_id=post_id)


def curtir_comentario(request, comentario_id):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        comentario = Comentario.objects.get(_id=ObjectId(comentario_id))

        if not Curtida.objects.filter(usuario=usuario, comentario_id=comentario).exists():
            Curtida.objects.create(usuario=usuario, comentario_id=comentario, post_id=None)

    return redirect('detalhe_post', post_id=comentario.post_id._id)


def admin_posts(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    try:
        autor = Usuario.objects.get(_id=ObjectId(usuario_id))

        if autor.tipo != 'psicologo':
            return HttpResponse("Apenas psicólogos podem acessar esta página.", status=403)

        posts = Post.objects.filter(autor=autor).order_by('-criado_em')
        
        for post in posts:
            post.id = str(post._id)  

    except Usuario.DoesNotExist:
        return redirect('login')

    return render(request, 'admin_psicologo.html', {
        'posts': posts,
        'autor': autor, 
    })


def novo_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES) 
        if form.is_valid():
            post = form.save(commit=False)
            usuario_id = request.session.get('usuario_id')
            if usuario_id:
                try:
                    autor = Usuario.objects.get(_id=ObjectId(usuario_id))
                    post.autor = autor
                    post.save()
                    return redirect('blog')
                except Usuario.DoesNotExist:
                    form.add_error(None, "Usuário não encontrado. Faça login novamente.")
            else:
                form.add_error(None, "Usuário não autenticado.")
    else:
        form = PostForm()
    return render(request, 'novo_post.html', {'form': form})



def editar_post(request, post_id):
    post = get_object_or_404(Post, _id=ObjectId(post_id))
    usuario_id = request.session.get('usuario_id')
    if not usuario_id or str(post.autor._id) != usuario_id:
        return HttpResponse("Você não tem permissão para editar este post.", status=403)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detalhe_post', post_id=post_id)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'editar_post.html', {
        'form': form,
        'post': post
    })


def excluir_post(request, post_id):
    post = get_object_or_404(Post, _id=ObjectId(post_id))
    usuario_id = request.session.get('usuario_id')

    if not usuario_id or str(post.autor._id) != usuario_id or post.autor.tipo != 'psicologo':
        return HttpResponse("Você não tem permissão para excluir este post.", status=403)

    if request.method == "POST":
        post.delete()
        return redirect('blog')
    return render(request, 'excluir_post.html', {'post': post})

def forum(request):
    return render(request, 'forum.html')
