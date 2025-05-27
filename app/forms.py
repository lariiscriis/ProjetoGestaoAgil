from django import forms
from app.models import Usuario, Post, Comentario
from django.contrib.auth.hashers import make_password
from ckeditor.widgets import CKEditorWidget

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
    conteudo = forms.CharField(widget=CKEditorWidget()) 
    class Meta:
        model = Post
        fields = ['titulo', 'conteudo', 'thumbnail']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'titulo'}),
            'conteudo': forms.Textarea(attrs={'placeholder': 'conteudo'}),  
            'thumbnail': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
          
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'placeholder': 'Escreva seu comentário aqui...'}),
        }