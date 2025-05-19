from django.db import models

class Usuario(models.Model):
    TIPO_USUARIO = [
        ('usuario', 'Usuário'),
        ('psicologo', 'Psicólogo'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    tipo = models.CharField(
    max_length=10,
    choices=[('usuario', 'Usuário'), ('psicologo', 'Psicólogo')],
    default='usuario')
    crp = models.CharField(max_length=20, null=True, blank=True)
    area_atuacao = models.TextField(null=True, blank=True)

