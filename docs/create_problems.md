⚙️ Automação de Criação de Problemas na API (create_problems.py)

Este guia detalha o processo de criação em massa de problemas no Juiz Online (Online Judge) a partir de arquivos JSON pré-formatados, usando o script create_problems.py.

📈 Visão Geral do Workflow

O processo de carregamento de problemas segue duas fases principais:

Preparação (JSON): Criação dos arquivos JSON, um para cada problema, contendo a descrição, limites de tempo/memória, casos de teste e o hash de comparação.

Criação (create_problems.py): O script autenticado lê todos os arquivos JSON no diretório configurado e envia requisições POST para o endpoint /v0/problems da API.

FASE 1: Configuração do Script e Ambiente

1. Pré-requisitos Python

Certifique-se de que você tem Python instalado e a biblioteca requests para comunicação HTTP com a API:

# Comando para instalar a dependência necessária
pip install requests


2. Configuração do Script (scripts/create_problems.py)

O script depende de três variáveis principais: a URL da API, o caminho para os arquivos JSON e o Token JWT para autenticação.

Variável        Exemplo
API_URL         http://127.0.0.1:8000/v0/problems

JSON_DIR        json-create-problems

JWT_TOKEN       <seu token gerado>

3. Estrutura dos Arquivos JSON

O diretório JSON_DIR deve conter todos os arquivos de problema no formato JSON, tipicamente um arquivo por problema. O conteúdo deve aderir ao schema esperado pelo payload do POST /v0/problems.

json-create-problems/
├── problema_a.json
├── problema_b.json
└── problema_c_nota.json
