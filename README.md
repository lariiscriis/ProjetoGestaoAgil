# Projeto de Gestao Agil

## Como rodar a aplicação localmente

### 1. Clone o repositório

```bash
  git clone https://github.com/seu-usuario/seu-projeto.git
  cd seu-projeto
```

### 2. Crie um ambiente virtual
```bash
python -m venv ambienteVirtual 
```

### 3. Ative o ambiente virtual
```bash
ambienteVirtual\Scripts\activate  
```


### 4. Instale as dependências
```bash
pip install -r requirements.txt
```


## 5. Configure o banco de dados MongoDB
#### No seu arquivo settings.py, edite a configuração do banco:

```bash
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'projetoGestaoAgil',
        'CLIENT': {
            'host': 'mongodb+srv://<usuario>:<senha>@<cluster>.mongodb.net/<nome_do_banco>?retryWrites=true&w=majority',
        }
    }
}
```


## Rodar a aplicação
1. Aplicar as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```


### 2. Iniciar o servidor

```bash
python manage.py runserver
```
