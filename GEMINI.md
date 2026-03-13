# Contexto do Gemini Code Assistant

## Visão Geral do Projeto

Este projeto é uma API de backend baseada em Python para um sistema de julgamento de competições de programação. Ele permite que os usuários enviem soluções para problemas de programação, que são então avaliadas por um serviço de "juiz" dedicado.

**Tecnologias Principais:**

*   **Backend:** Python com o framework FastAPI.
*   **Banco de Dados:** MongoDB para armazenar dados relacionados a usuários, problemas e submissões.
*   **Fila de Tarefas:** RQ (Redis Queue) com broker Redis para gerenciar o julgamento assíncrono de submissões.
*   **Conteinerização:** Docker e Docker Compose são usados para orquestrar os diferentes serviços (API, worker, juiz e banco de dados).
*   **Gerenciamento de Dependências:** Poetry é usado para gerenciar as dependências do Python.

**Arquitetura:**

O sistema é composto por quatro serviços principais:

*   `api`: A aplicação FastAPI principal que expõe os endpoints da API RESTful.
*   `worker`: Um worker Celery que consome tarefas de submissão da fila Redis.
*   `judge`: Um serviço dedicado que executa o código enviado em um ambiente sandbox e avalia a saída. Este serviço é construído a partir do `Dockerfile.judge` e inclui runtimes para várias linguagens de programação.
*   `mongo`: Uma instância do MongoDB para persistência de dados.

## Compilando e Executando

### Configuração Inicial

1.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Instale as dependências usando o Poetry:**
    ```bash
    pip install poetry
    poetry install
    ```

### Executando a Aplicação

*   **Inicie todos os serviços com o Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```
    A API estará disponível em `http://127.0.0.1:8000/docs#/`.

### Testes e Linting

*   **Execute o linter:**
    ```bash
    poetry run blue .
    ```
    Este projeto usa `blue` para linting e formatação.

*   **Teste de Estresse:**
    O diretório `k6_testing` contém uma configuração básica de teste de estresse usando k6.

## Convenções de Desenvolvimento

*   **Estilo de Código:** O projeto usa `blue` para linting e formatação. O `Makefile` fornece um comando `lint` para impor o estilo.
*   **Configuração:** A configuração da aplicação é gerenciada usando `pydantic-settings` e é carregada de um arquivo `local.env`. A configuração principal está em `src/config.py`.
*   **Modularidade:** A aplicação é bem estruturada, com uma clara separação de responsabilidades. Os roteadores são definidos em `src/routers.py` e são carregados dinamicamente pela aplicação principal em `src/app.py`. Cada recurso (por exemplo, `users`, `problems`, `submissions`) tem seu próprio módulo dedicado com controladores, modelos e repositórios.
*   **Tipagem:** O código usa extensivamente as dicas de tipo do Python.
*   **Autenticação:** A API usa um token JWT para autenticação. O arquivo `README.md` fornece instruções sobre como gerar um token para fins de teste. A chave de API mestre é definida no arquivo `.env`.