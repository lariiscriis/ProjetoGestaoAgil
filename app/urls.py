from django.urls import path
from . import views


urlpatterns = [
    path('', views.app, name='app'),
    path('ajuda/', views.linkAjuda, name='linkAjuda'),
    path('login/', views.login_view, name='login'),
    path('usuarios', views.exibirUsuarios , name = "exibirUsuarios"),
<<<<<<< HEAD
    path('forum/', views.forum, name='forum'),
    
=======

>>>>>>> 6bccab372e6548ec61d03c7eef2942a5760e644d
    path('blog', views.blog, name='blog'),
    path('post/<str:post_id>/', views.detalhe_post, name='detalhe_post'),
    path('novo_post/', views.novo_post, name='novo_post'),
    path('post/<str:post_id>/editar/', views.editar_post, name='editar_post'),
    path('post/<str:post_id>/excluir/', views.excluir_post, name='excluir_post'),
]