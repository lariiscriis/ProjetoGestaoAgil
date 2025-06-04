from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from .forms import CadastroForm, LoginForm, CadastroPsicologoForm, PostForm, ComentarioForm, ForumForm, EditarPerfilForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Post, Comentario, Curtida, Forum
from bson import ObjectId 
from django.contrib.auth.decorators import login_required
from collections import Counter
from django.db.models import Q

def app(request):
    return render(request, 'landing-page.html')

def linkAjuda(request):
    psicologos = Usuario.objects.filter(tipo='psicologo')
    return render(request, 'ajuda.html', {'psicologos': psicologos})

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

def logout(request):
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    return redirect('app')


def exibirUsuarios(request):
    usuarios = Usuario.objects.all().values()
    return render(request, "usuarios.html", {'listUsuarios': usuarios})

# # Blog Views 
def blog(request):
    query = request.GET.get('q', '')
    autor_id = request.GET.get('autor_id')
    usuario = None
    usuario_id = request.session.get('usuario_id')

    if usuario_id:
        try:
            usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        except Usuario.DoesNotExist:
            pass

    if query:
        posts = Post.objects.filter(
            Q(titulo__icontains=query) | Q(conteudo__icontains=query)
        ).select_related('autor')
    elif autor_id:
        try:
            posts = Post.objects.filter(autor=ObjectId(autor_id)).select_related('autor')
        except Exception:
            posts = Post.objects.none()
    else:
        posts = Post.objects.select_related('autor').all()

    # Contar curtidas por post
    curtidas_por_post = Counter()
    for curtida in Curtida.objects.filter(post__isnull=False):
        if curtida.post:
            curtidas_por_post[curtida.post._id] += 1

    # Ordenar os posts mais curtidos pro carrossel
    Allposts = Post.objects.select_related('autor').all()
    posts_com_curtidas = sorted(
        Allposts,
        key=lambda post: curtidas_por_post.get(post._id, 0),
        reverse=True
    )

    top_mais_curtidos = posts_com_curtidas[:6]

    # Autores mais frequentes
    contagem_autores = Counter()
    for post in posts:
        contagem_autores[post.autor] += 1
    autores_ordenados = sorted(contagem_autores.items(), key=lambda item: item[1], reverse=True)[:5]
    autores_frequentes = [{'autor': autor, 'total': total} for autor, total in autores_ordenados]

    return render(request, 'blog.html', {'posts': posts,'usuario': usuario,'autores_frequentes': autores_frequentes,'request': request,'top_mais_curtidos': top_mais_curtidos})

def detalhe_post(request, post_id):
    post = get_object_or_404(Post, _id=ObjectId(post_id))
    comentarios = Comentario.objects.filter(post=post, comentario_pai=None).order_by('-data_criacao')


    form = ComentarioForm()
    usuario_id = request.session.get('usuario_id')
    
    if request.method == 'POST' and usuario_id:
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post = post  # era comentario.post_id
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

        if not Curtida.objects.filter(usuario=usuario, post=post).exists():
            Curtida.objects.create(usuario=usuario, post=post, comentario=None)

    return redirect('detalhe_post', post_id=post_id)


def curtir_comentario(request, comentario_id):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        comentario = Comentario.objects.get(_id=ObjectId(comentario_id))

    if not Curtida.objects.filter(usuario=usuario, comentario=comentario).exists():
        Curtida.objects.create(usuario=usuario, comentario=comentario, post=None)


    return redirect('detalhe_post', post_id=comentario.post._id)


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
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    try:
        autor = Usuario.objects.get(_id=ObjectId(usuario_id))
        if autor.tipo != 'psicologo':
            return HttpResponse("Apenas psicólogos podem criar posts.", status=403)
    except Usuario.DoesNotExist:
        return redirect('login')
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = autor
            post.save()
            return redirect('blog')
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
            if not post.thumbnail:
                post.thumbnail = 'defaults/default_thumbnail.jpeg'
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
    forums = Forum.objects.all().order_by('-data')
    usuario = None
    usuario_id = request.session.get('usuario_id')

    if usuario_id:
        try:
            usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        except Usuario.DoesNotExist:
            usuario = None

    # TRATAR O POST
    if request.method == "POST" and usuario:
        conteudo = request.POST.get('conteudo')
        if conteudo:
            Forum.objects.create(autor=usuario, conteudo=conteudo)
            return redirect('forum')

    return render(request, 'forum.html', {'forums': forums, 'usuario': usuario})
 
def novo_forum(request):
    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save(commit=False)
            usuario_id = request.session.get('usuario_id')
            if usuario_id:
                try:
                    try:
                        autor = Usuario.objects.get(_id=ObjectId(usuario_id))
                    except Usuario.DoesNotExist:
                        autor = None
 
                    if autor:
                        forum.autor = autor
                        forum.save()
                        return redirect('forum')
                    else:
                        form.add_error(None, "Usuário não encontrado. Faça login novamente.")
                except Exception as e:
                    form.add_error(None, f"Erro ao buscar usuário: {e}")
            else:
                form.add_error(None, "Usuário não autenticado.")
    else:
        form = ForumForm()
    return render(request, 'novo_forum.html', {'form': form})
 
def excluir_forum(request, forum_id):
    forum = get_object_or_404(Forum, _id=ObjectId(forum_id))
    usuario_id = request.session.get('usuario_id')
 
    if not usuario_id or str(forum.autor._id) != usuario_id:
        return HttpResponse("Você não tem permissão para excluir este forum.", status=403)
 
    if request.method == "POST":
        forum.delete()
        return redirect('forum')
    return render(request, 'excluir_forum.html', {'forum': forum})

def perfil_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não encontrado.", status=404)

    posts = Post.objects.filter(autor=usuario).order_by('-criado_em')
    comentarios = Comentario.objects.filter(autor=usuario).order_by('-data_criacao')

    return render(request, 'perfil_usuario.html', {
        'usuario': usuario,
        'posts': posts,
        'comentarios': comentarios
    })


def editar_perfil(request, usuario_id):
    usuario = get_object_or_404(Usuario, _id=ObjectId(usuario_id))

    if request.session.get('usuario_id') != str(usuario._id):
        return HttpResponse("Você não tem permissão para editar este perfil.", status=403)
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            if not usuario.foto_perfil:
                usuario.foto_perfil = 'defaults/default_foto.png'
            if not usuario.background_perfil:
                usuario.background_perfil = 'defaults/default_background.jpg'
            if form.cleaned_data['senha']:
               usuario.senha = make_password(form.cleaned_data['senha'])
            form.save()
            return redirect('perfil_usuario', usuario_id=usuario_id)
    else:
        form = EditarPerfilForm(instance=usuario)

    return render(request, 'editar_perfil.html', {'form': form, 'usuario': usuario})