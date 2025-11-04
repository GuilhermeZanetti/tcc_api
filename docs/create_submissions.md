# Como enviar submissions automaticamente

# 1. Abra [create_submissions.py](../scripts/create_submissions.py)
# 2. Altere o diretório 
Em `SUBMISSIONS_DIR` coloque o caminho completo até os códigos enviados pelos alunos
Em `PROBLEM_ID` coloque o ID do problema
Em `LANGUAGE` coloque a linguagem do problema (`py`,`c`,`cpp`, etc)

# 3. Autentique-se na API
No endpoint de autenticação, copie o `access_token`

# 4. Rode a automação
Execute:
```shell
python scripts/create_submissions.py {COLE SEU TOKEN JWT AQUI}
```

# 5. Copie os resultados da API (submissions)
1. Crie o arquivo `problem{Letra}_{linguagem}.json`
1. Altere o arquivo [submissions_to_csv](../scripts/transform-json-into-csv/submissions_to_csv.py)
1.1. Variavel `json_filename`
1.1. Rode a automação com: 

```shell
python /scripts/transform-json-into-csv/submissions_to_csv.py
```

# 6. Entre no site Google Sheets e Importe o arquivo
