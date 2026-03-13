🤖 Automação de Submissões e Geração de Resultados

Este guia detalha o processo de submissão em massa de códigos-fonte para a API do Juiz Online, coleta dos resultados finais (status de Accepted, WA, CE, etc.), e exportação desses dados para análise do TCC.

O fluxo é gerenciado por dois scripts principais: create_submissions.py (Submissão e Polling) e submissions_to_csv.py (Conversão para CSV).

# 📈 Visão Geral do Workflow

O processo de submissão e validação é dividido em três etapas críticas:

Submissão (create_submissions.py): O script autenticado lê os arquivos de código-fonte, codifica-os em Base64 e os envia para a API, que enfileira o julgamento.

Processamento (API/Worker): A API monitora o resultado de cada submissão (polling) até que o status final seja determinado (ACCEPTED, WA, RE, TLE, etc.).

Análise (submissions_to_csv.py): Após a conclusão da submissão em massa, os resultados são extraídos da API e processados em um formato CSV para facilitar a análise.

FASE 1: Configuração do Script e Ambiente

1. Pré-requisitos Python

Certifique-se de que você tem Python instalado e a biblioteca requests para comunicação HTTP com a API:

# Comando para instalar a dependência necessária


2. Configuração do Script (scripts/create_submissions.py)

É obrigatório editar as variáveis de configuração no topo do arquivo scripts/create_submissions.py para mapear seu ambiente local e os problemas a serem testados:

Variável                                    Exemplo                                                                                                                      
API_BASE_URL                                http://127.0.0.1:8000/v0

SUBMISSIONS_DIR                             /home/user/meu_tcc/testes-outras-linguagens

PROBLEM_ID_BY_PATH_NAME                     "A": "abad3db3-0f6a-4834-88e0-fd7ca0f42470"

3. Estrutura dos Códigos-Fonte

O diretório SUBMISSIONS_DIR deve conter subdiretórios com os nomes dos problemas, e os arquivos de código dentro. A extensão do arquivo define a linguagem de submissão (e.g., .py, .go, .java, .cs, .php, .js):

SUBMISSIONS_DIR/
├── A/
│   ├── accepted.py
│   ├── ce_exemplo.java
│   └── wa_simples.go
├── B/
│   ├── accepted.cpp
│   └── pe_extra_space.php
└── ...


FASE 2: Execução da Automação

1. Obtenção do Token JWT

O script exige autenticação Bearer para autorizar a submissão de códigos.

Acesse o endpoint de autenticação da sua API: POST /auth/integrator-token.

Copie o valor do access_token (JWT) gerado.

2. Rodar a Submissão

Execute o script create_submissions.py, passando o token JWT copiado como argumento de linha de comando.

Execute este comando a partir da raiz do projeto:

# Substitua {COLE_SEU_TOKEN_JWT_AQUI} pelo token real
```
python scripts/create_submissions.py {COLE_SEU_TOKEN_JWT_AQUI}
```

O script irá:

Ler e codificar cada arquivo.

Enviar para a API e obter o ID da submissão.

Fazer polling contínuo para cada ID até o status final.

Imprimir o resultado no console.

FASE 3: Coleta de Resultados e Exportação para CSV

Após a execução do create_submissions.py (FASE 2) ter terminado, siga os passos para extrair os resultados consolidados para análise.

1. Obter e Salvar o JSON Completo da API

Use o endpoint da API para listar todas as submissions processadas (geralmente GET /v0/submissions).

Copie o JSON de resposta completo da API.

Crie um novo arquivo JSON na pasta scripts/transform-json-into-csv/ (ex: lote_teste_1_go_php_cs.json). Cole o JSON copiado nesse arquivo.

2. Gerar o CSV

Abra o script de transformação: scripts/transform-json-into-csv/submissions_to_csv.py.

Ajuste a variável json_filename dentro do script para o nome do arquivo JSON que você acabou de criar (ex: lote_teste_1_go_php_cs.json).

Execute a automação para gerar o CSV a partir da raiz do projeto:

# Executa o script de conversão de JSON para CSV
python scripts/transform-json-into-csv/submissions_to_csv.py


O arquivo de saída (ex: results_lote_teste_1_go_php_cs.csv) será gerado na mesma pasta.

3. Análise dos Dados

Importe o arquivo CSV gerado no Google Sheets ou Excel para realizar a análise estatística.

# 🧹 FASE 4: Limpeza do Banco de Dados (MongoDB)

Para iniciar uma nova bateria de testes do zero, você deve limpar todas as submissões anteriores do banco de dados (MongoDB) do juiz.

Siga os passos, substituindo <nome_ou_id_do_container_mongo> pelo identificador do seu container (obtido via docker ps).

## 1. Encontre o nome do seu container Mongo 
```
docker ps 
```

## 2. Acesse o shell Mongo DENTRO do container
```
docker exec -it <nome_ou_id_do_container_mongo> mongosh
```

## 3. No shell Mongo, execute os comandos:

```shell
use judge
db.submissions.deleteMany({})
exit
```

## 4. Saia do container
```
 exit
```