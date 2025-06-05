from django.urls import path
from . import views


urlpatterns = [
    path('', views.app, name='app'),
    path('ajuda/', views.linkAjuda, name='linkAjuda'),
    path('login/', views.login_view, name='login'),

    path('usuarios', views.exibirUsuarios , name = "exibirUsuarios"),

    path('forum/', views.forum, name='forum'),
    path('novo_forum/', views.novo_forum, name='novo_forum'),
    path('forum/<str:forum_id>/excluir/', views.excluir_forum, name='excluir_forum'),
    
    path('blog', views.blog, name='blog'),
    path('post/<str:post_id>/', views.detalhe_post, name='detalhe_post'),
    path('novo_post/', views.novo_post, name='novo_post'),
    path('post/<str:post_id>/editar/', views.editar_post, name='editar_post'),
    path('post/<str:post_id>/excluir/', views.excluir_post, name='excluir_post'),

    path('curtir_comentario/<str:comentario_id>/', views.curtir_comentario, name='curtir_comentario'),
    path('curtir_post/<str:post_id>/', views.curtir_post, name='curtir_post'),
    path('excluir_comentario/<str:comentario_id>/excluir', views.excluir_comentario, name='excluir_comentario'),

    path('admin/posts/', views.admin_posts, name='admin_posts'),

    path('perfil/<str:usuario_id>/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/<str:usuario_id>/editar/', views.editar_perfil, name='editar_perfil'),

    path('logout/', views.logout, name='logout'),
    path('notificacoes/', views.notificacoes_view, name='notificacoes'),


]