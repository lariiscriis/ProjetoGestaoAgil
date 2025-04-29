from django.urls import path
from . import views


urlpatterns = [
    path('', views.app, name='app'),
    path('ajuda/', views.linkAjuda, name='linkAjuda'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('usuarios', views.exibirUsuarios , name = "exibirUsuarios"),

]