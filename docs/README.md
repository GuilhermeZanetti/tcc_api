# Judge API
A Judge API é o motor responsável por processar e avaliar submissões de código em um ambiente de maratona de programação.
Este guia foi criado para que qualquer pessoa consiga subir o projeto do zero, de forma simples e direta.
## Setup
# **Aqui é a aba onde vamos seguir os passos para rodar o projeto!**

## **Execute comando a comando**

1. Crie um ambiente virtual

```
python3 -m venv venv
```

2. Ative o ambiente virtual

```
source venv/bin/activate(Linux / MacOS)
.\venv\Scripts\activate (Windows)
```

3. Dentro do ambiente virtual, instale o Poetry, responsável por gerenciar as dependências do projeto:

```
pip install poetry
```

4. Instale as dependências do projeto
Use o Poetry para instalar automaticamente todas as dependências listadas em pyproject.toml
```
poetry install
```

5. Inicializando os Serviços com Docker
Após instalar as dependências, suba os containers necessários (API, MongoDB, etc.):

```bash
docker-compose up -d --build
```
Isso irá compilar as imagens e iniciar todos os serviços em segundo plano.

6. Acesse a API
Após o Docker estar em execução, acesse a documentação interativa da API via Swagger UI:

```bash
http://127.0.0.1:8000/docs#/
```

7. Gerar Token de Autenticação (via API)
A geração do token JWT é feita diretamente pela própria API.

```
Acesse a rota:
POST /auth/integrator-token

No corpo da requisição (Request body), envie o seguinte JSON:
"api_key": "57fba00c-aa3d-4009-87d6-700f58a4032b"

Clique em Execute (ou envie via Postman/Insomnia).
Se a chave for válida, você receberá uma resposta semelhante a:

  "access_token": "<seu_token_jwt>",
  "token_type": "bearer"

Copie o valor de access_token e use nas requisições autenticadas:
Authorization: Bearer <seu_token_jwt>


```

### Executando Testes

Com a aplicação rodando, você pode executar os testes usando `pytest`:

```bash
poetry run pytest
```

8. Comandos de Migração (MongoDB)
Para aplicar migrations no banco de dados, utilize os comandos abaixo.
  ```
  (Upgrade (aplicar migrações))
  docker-compose exec judge mongodb-migrate \
  --url 'mongodb://mongodb:27017/judge?replicaSet=rs0' \
  --migrations migrations \
  --database judge

  Downgrade (reverter migrações)
  docker-compose exec judge mongodb-migrate --downgrade \
  --url 'mongodb://mongodb:27017/judge?replicaSet=rs0' \
  --migrations migrations \
  --database judge
  ```

9. Inserindo Credenciais no Banco (MongoDB)
Execute o seguinte comando no MongoDB para cadastrar o acesso da API externa:

  ```
  db.authentication.insertOne({
    "id": "3dcf5b22-b2a2-4c0a-88f5-f4b787728c8f",
    "name": "Maratona",
    "hashed_api_key": "57fba00c-aa3d-4009-87d6-700f58a4032b",
    "is_active": true,
    "permissions": [
      "read:problems",
      "read:submissions",
      "create:problems",
      "create:submissions",
      "update:problems",
      "update:submissions",
      "delete:problems",
      "delete:submissions"
    ],
    "created_at": ISODate(),
    "updated_at": ISODate()
  })
  ```