import argparse
import base64
import os
import time
import requests
import sys

# --- Configuração ---
API_BASE_URL = "http://localhost:8000" 
API_VERSION_PREFIX = "/v0"
DEFAULT_API_KEY = "57fba00c-aa3d-4009-87d6-700f58a4032b"

# Mapeamento: Nome no Arquivo -> Código na API
LANGUAGE_MAP = {
    "C": "c",           # Regra: Arquivo diz C, usa compilador C (mesmo se extensão for .cpp)
    "C++": "cpp",
    "CPP": "cpp",
    "CXX": "cpp",
    "C-11": "cpp",      # Regra específica C-11 -> C++
    "Python2": "py",
    "Python3": "py",
    "Java": "java",
    "JavaScript": "js",
    "JS": "js",
    "Go": "go",
    "C#": "csharp",
    "CS": "csharp",
    "PHP": "php"
}

def authenticate(api_key: str) -> str:
    """
    Realiza a autenticação usando a API Key e retorna o Bearer Token.
    """
    print(f"🔑 Autenticando com API Key: {api_key[:5]}...")
    
    url = f"{API_BASE_URL}/auth/integrator-token"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {"api_key": api_key}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        
        if not token:
            print("❌ Erro: A resposta da autenticação não contém 'access_token'.")
            sys.exit(1)
            
        print("✅ Autenticação realizada com sucesso!")
        return token

    except requests.exceptions.RequestException as e:
        print(f"❌ Falha na autenticação: {e}")
        if e.response:
            print(f"   Detalhes: {e.response.text}")
        sys.exit(1)

def get_problem_map(token: str) -> dict[str, str]:
    """
    Busca problemas na API e mapeia a Letra (A, B...) para o UUID.
    Baseado no JSON: "name": "Problema A: Nota de Algoritmos"
    """
    print("🔄 Buscando lista de problemas na API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}{API_VERSION_PREFIX}/problems", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        problem_map = {}
        results = data.get("results", [])
        
        print(f"📋 Analisando {len(results)} problemas retornados...")

        for problem in results:
            name = problem.get("name", "").strip()
            problem_id = problem.get("id")
            
            if not name:
                continue

            # Normaliza para facilitar o parse
            # Ex: "Problema A: Nota..." -> ["PROBLEMA", "A", "NOTA..."]
            parts = name.upper().replace(":", " ").split()
            
            identifier = None
            
            # Lógica para encontrar a letra
            if len(parts) >= 2 and parts[0] in ["PROBLEMA", "PROBLEM"]:
                # Pega a segunda palavra como identificador (Ex: "A")
                identifier = parts[1]
            elif len(parts) == 1 and len(parts[0]) == 1:
                # Caso o nome seja apenas "A"
                identifier = parts[0]
            
            if identifier:
                problem_map[identifier] = problem_id
                # Debug para confirmar o mapeamento correto
                # print(f"   [MAP] '{identifier}' -> {name} ({problem_id})")
            else:
                print(f"   ⚠️ Não foi possível extrair letra de: '{name}'")

        print(f"✅ {len(problem_map)} letras de problemas mapeadas com sucesso.")
        return problem_map

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar problemas: {e}")
        sys.exit(1)

def parse_filename(filename: str) -> tuple[str, str, str] | None:
    """
    Extrai metadados do nome do arquivo ignorando a extensão.
    """
    # Remove a extensão para a lógica focar apenas no nome
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split('-')
    
    # O formato mínimo esperado é {Prob}-{Lang}-{Equipe}
    if len(parts) < 3:
        return None

    problem_letter = parts[0].upper()
    
    # Lógica Especial: C-11
    # Se o nome for tipo "B-C-11-equipe03..."
    if len(parts) > 3 and parts[1] == 'C' and parts[2] == '11':
        raw_language = "C-11"
        # A equipe estará deslocada uma posição
        team_name = parts[3] 
    else:
        raw_language = parts[1]
        team_name = parts[2]
    
    # Mapeia a linguagem baseada no nome (raw_language), ignorando a extensão do arquivo
    api_lang = LANGUAGE_MAP.get(raw_language)
    
    if not api_lang:
        # print(f"⚠️  Linguagem '{raw_language}' não suportada (Arquivo: {filename})")
        return None
        
    return problem_letter, api_lang, team_name

def submit_code(file_path: str, problem_id: str, language_type: str, token: str):
    """Lê o arquivo, converte para Base64 e envia para a API."""
    filename = os.path.basename(file_path)
    
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            encoded_content = base64.b64encode(content).decode("utf-8")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {filename}: {e}")
        return

    payload = {
        "problem_id": problem_id,
        "language_type": language_type,
        "content": encoded_content
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        print(f"🚀 Enviando {filename}...")
        # print(f"   ↳ Prob ID: {problem_id[:8]}... | Lang API: {language_type}")
        
        response = requests.post(f"{API_BASE_URL}{API_VERSION_PREFIX}/submissions", json=payload, headers=headers)
        
        if response.status_code == 201:
            # data = response.json()
            print(f"   ✅ Sucesso!")
        elif response.status_code == 409:
            print("   ⚠️  Conflito (409): Problema não existe ou erro de regra de negócio.")
        elif response.status_code == 422:
            print(f"   ❌ Erro 422 (Validação): Verifique o payload.")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

def main():
    parser = argparse.ArgumentParser(description="Importador de Submissões CodeJudge")
    parser.add_argument("directory", help="Caminho da pasta com as submissões")
    parser.add_argument("--api-key", help="Chave de API do Integrador", default=DEFAULT_API_KEY)
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"❌ Diretório não encontrado: {args.directory}")
        sys.exit(1)

    # 1. Autentica
    token = authenticate(args.api_key)

    # 2. Cria o mapa Letra -> UUID
    problem_map = get_problem_map(token)

    print("-" * 60)
    print(f"📂 Iniciando varredura em: {args.directory}")
    
    count_enviados = 0
    
    # 3. Varredura Recursiva
    for root, dirs, files in os.walk(args.directory):
        # Ordena para processar em ordem alfabética
        for filename in sorted(files):
            if filename.startswith('.'):
                continue

            file_path = os.path.join(root, filename)
            
            # Parseia o nome
            parsed = parse_filename(filename)
            if not parsed:
                continue
                
            prob_letter, api_lang, team = parsed
            
            # Busca o ID do problema usando a letra extraída
            problem_id = problem_map.get(prob_letter)
            
            if not problem_id:
                print(f"⚠️  Arquivo {filename}: Problema '{prob_letter}' não encontrado na API. Pulei.")
                continue

            # Envia
            submit_code(file_path, problem_id, api_lang, token)
            count_enviados += 1
            
            # Pequeno delay para não sobrecarregar
            time.sleep(0.05)

    print("-" * 60)
    print(f"🏁 Finalizado. {count_enviados} submissões processadas.")

if __name__ == "__main__":
    main()