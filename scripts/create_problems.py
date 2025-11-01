import os
import json
import requests

# Defina a URL da sua API
API_URL = "http://127.0.0.1:8000/v0/problems"

# Diretório contendo os arquivos JSON dos problemas
JSON_DIR = "json-create-problems"

# Token JWT para autenticação
# Você pode obter o token fazendo uma requisição POST para http://127.0.0.1:8000/auth/integrator-token
# com o corpo: {"api_key": "57fba00c-aa3d-4009-87d6-700f58a4032b"}
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZGNmNWIyMi1iMmEyLTRjMGEtODhmNS1mNGI3ODc3MjhjOGYiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6c3VibWlzc2lvbnMiLCJyZWFkOnByb2JsZW1zIiwiY3JlYXRlOnN1Ym1pc3Npb25zIiwiY3JlYXRlOnByb2JsZW1zIiwidXBkYXRlOnN1Ym1pc3Npb25zIiwidXBkYXRlOnByb2JsZW1zIiwiZGVsZXRlOnByb2JsZW1zIiwicmVhZDpzdWJtaXNzaW9ucyJdLCJleHAiOjE3NjIxMDM5MzJ9.M_M2v8NNCK1LNnyDHFLdXZs8sQiFCVFavIppMMke7E0"

if not JWT_TOKEN:
    print("Erro: O token JWT não foi fornecido.")
    print("Defina a variável de ambiente 'JWT_TOKEN' ou edite o script para incluí-lo.")
    exit(1)

headers = {"Authorization": f"Bearer {JWT_TOKEN}", "Content-Type": "application/json"}


def create_problems():
    """
    Lê os arquivos JSON do diretório 'json-create-problems' e cria os problemas
    via API.
    """
    for filename in os.listdir(JSON_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(JSON_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                problem_data = json.load(f)

            print(f"Criando problema a partir de {filename}...")
            try:
                response = requests.post(API_URL, headers=headers, json=problem_data)

                if response.status_code == 201:
                    print(f"  Problema '{problem_data['name']}' criado com sucesso!")
                else:
                    print(f"  Erro ao criar o problema '{problem_data['name']}'.")
                    print(f"  Status: {response.status_code}")
                    print(f"  Resposta: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"  Ocorreu um erro de conexão: {e}")


if __name__ == "__main__":
    create_problems()
