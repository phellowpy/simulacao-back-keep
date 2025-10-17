# 📦 KeepInventory: Sistema de Inventário Simplificado

Uma aplicação web simples e robusta para gerenciamento de inventário, focada em **criar, editar, excluir e listar produtos** rapidamente. Utiliza o **Firebase Realtime Database** para armazenamento em tempo real e o **Flask** para o backend da API.

---

## ✨ Funcionalidades

- ✅ Cadastro de Produtos: **Nome, Marca, Categoria, Prateleira e Preço**.
- 🛡️ **Filtro Agressivo de Conteúdo:** Recusa palavras ofensivas nos campos de texto.
- 🚫 **Validação de Nome:** Permite no máximo duas palavras no campo "Nome do Produto" (Nome e Sobrenome) e impede palavras repetidas seguidas (ex: "Água Água").
- ✍️ **Edição** completa de registros.
- 🗑️ **Exclusão** de produtos do inventário.
- 💾 Todos os dados são persistidos em tempo real no **Firebase Realtime Database**.
- 💻 Interface moderna com HTML/CSS e lógica em Python/Flask.

---

## 🚀 Tecnologias Utilizadas

| Componente | Tecnologia | Badge |
| :--- | :--- | :--- |
| **Backend (API)** | **Python (Flask)** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) |
| **Banco de Dados** | **Firebase Realtime DB** | ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=white) |
| **Frontend** | **HTML, CSS, JavaScript** | ![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JS](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |

---

## ⚙️ Como Rodar o Projeto

### 1. Pré-requisitos

Certifique-se de ter o Python 3 instalado e o `pip` (gerenciador de pacotes).

### 2. Configuração do Ambiente

1.  **Clone o repositório** ou navegue até a pasta do projeto.
2.  **Instale as dependências Python** (o código atualizado utiliza `better-profanity`):
    ```bash
    pip install flask flask-cors firebase-admin better-profanity
    ```

### 3. Configuração do Firebase

1.  Crie um projeto no Firebase e configure o **Realtime Database**.
2.  Vá em `Configurações do Projeto` > `Contas de Serviço` > `Gerar nova chave privada`.
3.  Renomeie o arquivo JSON baixado para `notas-keep-inventory-firebase-adminsdk-fbsvc-ae6fa3346d.json` e coloque-o na raiz do projeto, ao lado do arquivo `app.py`.

### 4. Execução

Execute o backend com o seguinte comando no terminal:

```bash
python app.py
