from django import forms
from app.models import Usuario

class CadastroForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome','class': 'input-padrao'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email','class': 'input-padrao'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Senha','class': 'input-padrao'}),
        }

class LoginForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'senha']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'input-padrao'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Senha','class': 'input-padrao'}),
        }