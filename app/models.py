from django.db import models
from djongo import models
from bson import ObjectId
from django.utils import timezone

class Usuario(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    background_perfil = models.ImageField(upload_to='background_perfil', null=True, blank=True,default='defaults/default_background.jpg')
    foto_perfil = models.ImageField(upload_to='foto_pefil', null=True, blank=True, default='defaults/default_foto.png')
    senha = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=[('usuario', 'Usuário'), ('psicologo', 'Psicólogo')], default='usuario')
    data_nascimento = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True, default='Essa bio está em construção... mas você já pode me conhecer melhor interagindo comigo!')
    telefone = models.CharField(max_length=15, null=True, blank=True)
    endereco = models.TextField(null=True, blank=True)

    crp = models.CharField(max_length=20, null=True, blank=True)
    area_atuacao = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    def __str__(self):
        return self.email
    
    def usuario_id(self):
        return str(self._id)

class Post(models.Model):
    _id = models.ObjectIdField(primary_key=True) 
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField() 
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='posts/thumbnails/', null=True, blank=True, default='defaults/default_thumbnail.jpeg')

    def __str__(self):
        return self.titulo
    
    def post_id(self):
        return str(self._id)

class Forum(models.Model):
    _id = models.ObjectIdField(primary_key=True) 
    conteudo = models.TextField()
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
 
    def forum_id(self):
        return str(self._id)
        
class Comentario(models.Model):
    _id = models.ObjectIdField(primary_key=True) 
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    forum = models.ForeignKey(Forum, null=True, blank=True, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    comentario_pai = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.texto
    def comentario_id(self):
        return str(self._id)
    
class Curtida(models.Model):
    _id = models.ObjectIdField(primary_key=True) 
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    forum = models.ForeignKey(Forum, null=True, blank=True, on_delete=models.CASCADE)
    comentario = models.ForeignKey(Comentario, null=True, blank=True, on_delete=models.CASCADE)
    data_curtida = models.DateTimeField(auto_now_add=True)
 
    def comcurtida_id(self):
        return str(self._id)
    
class Notificacao(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificacoes')
    autor_acao = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='notificacoes_realizadas')
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    comentario = models.ForeignKey(Comentario, null=True, blank=True, on_delete=models.CASCADE)
    comentario_pai = models.ForeignKey(Comentario, null=True, blank=True, on_delete=models.CASCADE, related_name='notificacoes_respostas')
    forum = models.ForeignKey('Forum', null=True, blank=True, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    link = models.URLField(blank=True, null=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo.title()} para {self.usuario.nome}'
