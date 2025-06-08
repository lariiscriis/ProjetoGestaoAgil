from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from .forms import CadastroForm, LoginForm, CadastroPsicologoForm, PostForm, ComentarioForm, ForumForm, EditarPerfilForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Post, Comentario, Curtida, Forum, Notificacao
from bson import ObjectId 
from django.contrib.auth.decorators import login_required
from collections import Counter
from django.db.models import Q
import requests
from django.shortcuts import render

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
                                if not usuario.ativo:
                                    return HttpResponse("Este perfil foi desativado.")

                            except Usuario.DoesNotExist:
                                usuario = None
                    else:
                        try:
                            usuario = Usuario.objects.get(email=email, tipo='usuario')
                            if not usuario.ativo:
                                return HttpResponse("Este perfil foi desativado.")

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

    top_mais_curtidos = posts_com_curtidas[:3]

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
            comentario.post = post
            comentario.autor = Usuario.objects.get(_id=ObjectId(usuario_id))
            
            comentario_pai_id = request.POST.get('comentario_pai_id')
            if comentario_pai_id:
                comentario_pai = Comentario.objects.get(_id=ObjectId(comentario_pai_id))
                comentario.comentario_pai = comentario_pai
                comentario.save()
                criar_notificacao_para_resposta(comentario)
            else:
                comentario.save()
                criar_notificacao_para_comentario(comentario)

            return redirect('detalhe_post', post_id=post_id)

    posts_do_autor = Post.objects.filter(autor=post.autor).exclude(_id=post._id)[:5]  

    return render(request, 'detalhe_post.html', {
        'post': post,
        'comentarios': comentarios,
        'form': form,
        'usuario_id': usuario_id,
        'posts_do_autor': posts_do_autor,
    })

def excluir_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, _id=ObjectId(comentario_id))
    usuario_id = request.session.get('usuario_id')

    if not usuario_id or str(comentario.autor._id) != usuario_id:
        return HttpResponse("Você não tem permissão para excluir este comentário.", status=403)

    comentario.delete()
    return redirect('perfil_usuario', usuario_id=usuario_id)


def curtir_post(request, post_id):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:

        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        post = Post.objects.get(_id=ObjectId(post_id))

        curtida, created = Curtida.objects.get_or_create(usuario=usuario, post=post, comentario=None)

        if not created:
            curtida.delete()
        else:
            criar_notificacao_curtida_post(post, usuario)
    else:
        return redirect('login')
    return redirect('detalhe_post', post_id=post_id)

def curtir_comentario(request, comentario_id):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        comentario = Comentario.objects.get(_id=ObjectId(comentario_id))
        curtida, created = Curtida.objects.get_or_create(usuario=usuario, comentario=comentario, post=None)

        if not created:
            curtida.delete()
        else:
            criar_notificacao_curtida_comentario(comentario, usuario)

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

from django.db.models import Prefetch

def forum(request):
    forums = Forum.objects.all().prefetch_related(
    Prefetch('comentarios', queryset=Comentario.objects.order_by('-data_criacao'))
).order_by('-data')

    usuario = None
    usuario_id = request.session.get('usuario_id')
    form = ForumForm()

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

    return render(request, 'forum.html', {'form': form, 'forums':forums, 'usuario': usuario})

 
def novo_forum(request):
    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save(commit=False)
            usuario_id = request.session.get('usuario_id')
            if usuario_id:
                try:
                    autor = Usuario.objects.get(_id=ObjectId(usuario_id))
                    forum.autor = autor
                    forum.save()
                    return redirect('forum.html')
                except Usuario.DoesNotExist:
                    form.add_error(None, "Usuário não encontrado. Faça login novamente.")
                except Exception as e:
                    form.add_error(None, f"Erro: {e}")
            else:
                form.add_error(None, "Usuário não autenticado.")
    else:
        form = ForumForm()
    
    posts = Forum.objects.all().order_by('-id')
    return render(request, 'forum.html', {'form': form, 'posts': posts})


def responder_forum(request, forum_id):
    if request.method == "POST":
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('login')


        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        forum = Forum.objects.get(_id=ObjectId(forum_id))
        texto = request.POST.get('texto')

        if texto:
            comentario = Comentario.objects.create(
                autor=usuario,
                texto=texto,
                forum=forum
            )
            criar_notificacao_resposta_forum(comentario, forum)
            return redirect('forum')

    return redirect('forum')


def curtir_forum(request, forum_id):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('login')

        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
        forum = Forum.objects.get(_id=ObjectId(forum_id))

        curtida, created = Curtida.objects.get_or_create(usuario=usuario, forum=forum)

        if not created:
            curtida.delete()
        else:
            criar_notificacao_curtida_forum(forum, usuario)

    return redirect('forum')

def excluir_forum(request, forum_id):
    forum = get_object_or_404(Forum, _id=ObjectId(forum_id))
    usuario_id = request.session.get('usuario_id')

    if not usuario_id or str(forum.autor._id) != usuario_id:
        return HttpResponse("Você não tem permissão para excluir este fórum.", status=403)

    if request.method == "POST":
        forum.delete()
        return redirect('forum.html')
    
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
            usuario = form.save(commit=False) 
            nova_senha = form.cleaned_data.get('senha')

            if nova_senha:
               usuario.senha = make_password(nova_senha)

            if not usuario.foto_perfil:
                usuario.foto_perfil = 'defaults/default_foto.png'
                
            if not usuario.background_perfil:
                usuario.background_perfil = 'defaults/default_background.jpg'

            # if form.cleaned_data['senha']:
            #    usuario.senha = make_password(form.cleaned_data['senha'])

            usuario.save()
            return redirect('perfil_usuario', usuario_id=usuario_id)
    else:
        form = EditarPerfilForm(instance=usuario)

    return render(request, 'editar_perfil.html', {'form': form, 'usuario': usuario})

def excluir_conta(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não encontrado.", status=404)

    if request.method == 'POST':
        usuario.ativo = False
        usuario.save()
        del request.session['usuario_id']
        return redirect('app')

    return render(request, 'excluir_conta.html', {'usuario': usuario})


def criar_notificacao_para_comentario(comentario):
    post = comentario.post
    if post and comentario.autor != post.autor:
        Notificacao.objects.create(
            usuario=post.autor,
            comentario=comentario,
            post=post,
            tipo='comentario',
            link=f"/post/{post._id}/"
        )
def criar_notificacao_para_resposta(resposta):
    comentario_pai = resposta.comentario_pai
    if comentario_pai and resposta.autor != comentario_pai.autor:
        Notificacao.objects.create(
            usuario=comentario_pai.autor,
            comentario=resposta,
            comentario_pai=comentario_pai,
            post=comentario_pai.post,
            tipo='resposta',
            link=f"/post/{comentario_pai.post._id}/"
        )

def criar_notificacao_curtida_post(post, quem_curtiu):
    if quem_curtiu != post.autor:
        Notificacao.objects.create(
            usuario=post.autor,
            autor_acao=quem_curtiu,
            post=post,
            tipo='curtida_post',
            link=f"/post/{post._id}/"
        )

def criar_notificacao_curtida_comentario(comentario, quem_curtiu):
    if quem_curtiu != comentario.autor:
        Notificacao.objects.create(
            usuario=comentario.autor,
            autor_acao=quem_curtiu,
            comentario=comentario,
            tipo='curtida_comentario',
            link=f"/post/{comentario.post._id}/"
        )

def criar_notificacao_curtida_forum(forum, quem_curtiu):
    if quem_curtiu != forum.autor:
        Notificacao.objects.create(
            usuario=forum.autor,
            autor_acao=quem_curtiu,
            forum=forum,
            tipo='curtida_forum',
            link=f"/forum/#forum-{forum._id}"
        )

def criar_notificacao_resposta_forum(comentario, forum):
    if comentario.autor != forum.autor:
        Notificacao.objects.create(
            usuario=forum.autor,
            comentario=comentario,
            forum=forum,
            tipo='resposta_forum',
            link=f"/forum/#comentario-{comentario.comentario_id}"
        )


def notificacoes_view(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(_id=ObjectId(usuario_id))
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não encontrado", status=404)

    notificacoes = Notificacao.objects.filter(usuario=usuario).order_by('-criada_em')
    return render(request, 'notificacoes.html', {'notificacoes': notificacoes})


def buscar_locais(request):
    resultados = []
    termo_busca = request.GET.get('q')
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lon')

    if termo_busca and latitude and longitude:
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': termo_busca,
            'format': 'json',
            'limit': 10,
            'viewbox': f"{float(longitude)-0.05},{float(latitude)+0.05},{float(longitude)+0.05},{float(latitude)-0.05}",
            'bounded': 1,
        }

        response = requests.get(url, params=params, headers={'User-Agent': 'meuapp/1.0'})
        if response.status_code == 200:
            resultados = response.json()

    dados_processados = [processar_resultado(local) for local in resultados]
    return render(request, 'buscar_locais.html', {
        'resultados': dados_processados,
        'termo_busca': termo_busca,
    })

def processar_resultado(local):
    partes = local['display_name'].split(', ')
    return {
        'nome': partes[0] if len(partes) > 0 else '',
        'rua': partes[1] if len(partes) > 1 else '',
        'bairro': partes[2] if len(partes) > 2 else '',
        'cidade': partes[-4] if len(partes) > 4 else '',
        'estado': partes[-2] if len(partes) > 2 else '',
        'cep': partes[-3] if len(partes) > 3 else '',
        'pais': partes[-1] if len(partes) > 1 else '',
        'lat': local['lat'],
        'lon': local['lon']
    }