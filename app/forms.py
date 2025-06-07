from django import forms
from app.models import Usuario, Post, Comentario, Forum
from django.contrib.auth.hashers import make_password
from django_summernote.widgets import SummernoteWidget
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date

class CadastroForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Senha'}),
            'tipo': forms.HiddenInput(attrs={'value': 'comum'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'usuario'
        user.senha = make_password(self.cleaned_data['senha'])
        if commit:
            user.save()
        return user

class CadastroPsicologoForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'tipo', 'crp', 'area_atuacao']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Senha'}),
            'tipo': forms.HiddenInput(attrs={'value': 'psicologo'}),
            'crp': forms.TextInput(attrs={'placeholder': 'CRP'}),
            'area_atuacao': forms.TextInput(attrs={'placeholder': 'Especialidades'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'psicologo'
        user.senha = make_password(self.cleaned_data['senha'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    crp = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'CRP',
            'class': 'input-padrao'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'input-padrao'
        })
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha',
            'class': 'input-padrao'
        })
    )

class PostForm(forms.ModelForm):
    conteudo = forms.CharField(widget=SummernoteWidget()) 
    class Meta:
        model = Post
        fields = ['titulo', 'conteudo', 'thumbnail']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'titulo'}),
            'thumbnail': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
          
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'placeholder': 'Escreva seu comentário aqui...'}),
        }

class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = [ 'conteudo']
        widgets = {
         'conteudo': forms.Textarea(attrs={'placeholder': 'Escreva seu comentário aqui...'}),
}

        

class EditarPerfilForm(forms.ModelForm):
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nova senha (deixe em branco para manter a atual)'
        }),
        required=False,
        min_length=8,
        help_text="A senha deve ter pelo menos 8 caracteres."
    )

    telefone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
        validators=[
            RegexValidator(r'^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$', 'Informe um telefone válido.'),
        ]
    )

    data_nascimento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'foto_perfil', 'background_perfil', 'senha',
                  'data_nascimento', 'bio', 'telefone', 'endereco', 'crp', 'area_atuacao']
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu email'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'background_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Conte um pouco sobre você'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Endereço completo'}),
            'crp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CRP (se for psicólogo)'}),
            'area_atuacao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Área de atuação'}),
        }

    def clean_data_nascimento(self):
        data = self.cleaned_data.get('data_nascimento')
        if data and data > date.today():
            raise ValidationError("A data de nascimento não pode ser no futuro.")
        return data