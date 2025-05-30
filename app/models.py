from django.db import models
from djongo import models
from bson import ObjectId
from django.utils import timezone

class Usuario(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    foto_perfil = models.ImageField(upload_to='media/', null=True, blank=True)
    senha = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=[('usuario', 'Usuário'), ('psicologo', 'Psicólogo')], default='usuario')
    data_nascimento = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    endereco = models.TextField(null=True, blank=True)

    crp = models.CharField(max_length=20, null=True, blank=True)
    area_atuacao = models.TextField(null=True, blank=True)

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
    thumbnail = models.ImageField(upload_to='posts/thumbnails/', null=True, blank=True)

    def __str__(self):
        return self.titulo
    
    def post_id(self):
        return str(self._id)
    

class Comentario(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    post_id = models.ForeignKey('Post', null=True, blank=True, on_delete=models.CASCADE)
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(default=timezone.now)
    comentario_pai = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    
    def comentario_id(self):
        return str(self._id)

class Curtida(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    post_id = models.ForeignKey('Post', null=True, blank=True, on_delete=models.CASCADE)
    comentario_id = models.ForeignKey('Comentario', null=True, blank=True,  on_delete=models.CASCADE)
    data_curtida = models.DateTimeField(default=timezone.now)