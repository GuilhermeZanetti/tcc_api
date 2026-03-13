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

Cada arquivo JSON deve seguir o schema esperado pelo endpoint `POST /v0/problems`. Exemplo de conteúdo:

```json
{
  "name": "Problema A: Nota de Algoritmos",
  "description": "Dado um conjunto de notas, calcule a média final do aluno.",
  "entry_description": "A primeira linha contém um inteiro N (1 ≤ N ≤ 100), seguido de N números reais.",
  "output_description": "Imprima a média com duas casas decimais.",
  "test_cases": [
    {
      "input_lines": ["3", "7.0 8.5 9.0"],
      "output_lines": ["8.17"]
    },
    {
      "input_lines": ["2", "5.0 10.0"],
      "output_lines": ["7.50"]
    }
  ]
}
```

FASE 2: Execução do Script

1. Obtendo o Token JWT

O script usa um token JWT fixo definido na variável `JWT_TOKEN` dentro do próprio arquivo `scripts/create_problems.py`. Antes de executar, obtenha um token válido:

```
POST /auth/integrator-token
Body: {"api_key": "57fba00c-aa3d-4009-87d6-700f58a4032b"}
```

Cole o valor de `access_token` retornado na variável `JWT_TOKEN` no script.

2. Executando o Script

Com o token configurado e os arquivos JSON no diretório `json-create-problems/`, execute a partir da raiz do projeto:

```bash
python scripts/create_problems.py
```

3. Saída Esperada

O script imprime o resultado de cada problema processado:

```
Criando problema a partir de problema_a.json...
  Problema 'Problema A: Nota de Algoritmos' criado com sucesso!
Criando problema a partir de problema_b.json...
  Problema 'Problema B: Ordenação' criado com sucesso!
```

Em caso de erro (ex: token inválido ou problema já existente), o script exibe o status HTTP e o corpo da resposta para diagnóstico.
