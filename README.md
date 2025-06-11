<p align="center">
  <img src="https://github.com/user-attachments/assets/eb3dd772-f2a7-43fe-b924-6f078ad1c20d" alt="logo amae" height="100" />
</p>

### Sobre O Amae


<table align="right">
  <tr>
    <td>
      <a href="https://youtu.be/MLz5p7NhT1c" target="_blank">
        <img src="https://github.com/user-attachments/assets/812686ca-e906-4ea6-803c-84229b7c9da4" alt="Assista no YouTube" width="330" />
      </a>
    </td>
  </tr>
  <tr>
    <td align="center">
      <em>Veja nosso pitch </em>
    </td>
  </tr>
</table>

<p align="left"  height="200" >
  O Amae é um projeto com viés acadêmico, desenvolvido por quatro estudantes da FATEC Praia Grande. 
  Nosso propósito é criar um espaço seguro para mães compartilharem vivências, receberem apoio e se fortalecerem juntas. 
  Acreditamos na troca de experiências como ferramenta de transformação e acolhimento. 
  Mais do que um projeto de estudo, Amae nasce do desejo genuíno de fazer a diferença na vida de quem enfrenta desafios diários.
  Assista ao vídeo no YouTube para entender melhor como funciona o projeto.
</p>



<h3 align="center">
  <a href="https://www.canva.com/design/DAGp1d5mwpY/zX_zcdXdGN3BPiKzMjafyg/view?utm_content=DAGp1d5mwpY&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h2ed47d385b" target="_blank" style="text-decoration: none; font-size: 1.5em;">
    🚀 Clique aqui para ver a apresentação no Canva
  </a>
</h3>

<p align="center">
  <a href="https://www.canva.com/design/DAGp1d5mwpY/zX_zcdXdGN3BPiKzMjafyg/view?utm_content=DAGp1d5mwpY&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h2ed47d385b" target="_blank">
    <img src="https://img.shields.io/badge/Ver%20Apresenta%C3%A7%C3%A3o%20no%20Canva-00C4CC?style=for-the-badge&logo=canva&logoColor=white" alt="Ver apresentação no Canva">
  </a>
</p>

<br>

### 🛠️ Tecnologias usadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![MongoDB Atlas](https://img.shields.io/badge/MongoDB%20Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)



### 🚀 Como rodar o projeto localmente
Siga os passos abaixo para configurar e executar o projeto na sua máquina:

### 1. Clone o repositório

```bash
  git clone https://github.com/lariiscriis/ProjetoGestaoAgil.git
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


### 5. Configure o banco de dados MongoDB
#### No seu arquivo settings.py no projeto, edite a configuração do banco:

```bash
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'nome_do_database',
        'CLIENT': {
            'host': 'mongodb+srv://<usuario>:<senha>@<cluster>.mongodb.net/<nome_do_banco>?retryWrites=true&w=majority',
        }
    }
}
```


### Rodar a aplicação
1. Aplicar as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Iniciar o servidor

```bash
python manage.py runserver
```

## 📌 Atenção

* Certifique-se de estar com o ambiente virtual ativo sempre que for rodar o projeto.
* Certifique-se de ter criado o banco na plataforma do mongodb atlas e criado o cluster para a configuração do banco no servidor

