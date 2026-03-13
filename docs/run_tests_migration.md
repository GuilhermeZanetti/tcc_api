# Importador de Submissões (run_tests_migration.py)

O script `scripts/run_tests_migration.py` automatiza a importação em massa de submissões de código a partir de arquivos organizados em um diretório local. Ele se autentica na API, mapeia automaticamente os problemas cadastrados (por letra, ex: "A", "B") e envia cada arquivo como uma submissão codificada em Base64.

## O que o script faz

1. Autentica-se via `POST /auth/integrator-token` usando a API Key configurada.
2. Busca a lista de problemas na API e mapeia a letra do problema (ex: "A") ao seu UUID.
3. Varre recursivamente o diretório informado, processando arquivos no formato `{Letra}-{Linguagem}-{Equipe}.{ext}` (ex: `A-Python3-equipe01.py`, `B-C++-time02.cpp`).
4. Para cada arquivo válido, envia uma submissão para `POST /v0/submissions`.

## Pré-requisitos

- API rodando em `http://localhost:8000` (ou ajuste `API_BASE_URL` no script).
- Biblioteca `requests` instalada (`pip install requests`).
- Problemas já cadastrados na API (use `scripts/create_problems.py` antes).
- Arquivos de submissão nomeados no formato `{Letra}-{Linguagem}-{Equipe}.{ext}`.

**Linguagens suportadas no nome do arquivo:** `Python3`, `Python2`, `C`, `C++`, `CPP`, `Java`, `JavaScript`, `JS`, `Go`, `C#`, `CS`, `PHP`, `C-11`

## Uso

```bash
# Usando a API Key padrão (definida no script)
python3 scripts/run_tests_migration.py /caminho/para/pasta/das/submissoes

# Especificando uma API Key diferente
python3 scripts/run_tests_migration.py /caminho/para/pasta/das/submissoes --api-key <sua-api-key>
```

## Saída esperada

```
🔑 Autenticando com API Key: 57fba...
✅ Autenticação realizada com sucesso!
🔄 Buscando lista de problemas na API...
📋 Analisando 5 problemas retornados...
✅ 5 letras de problemas mapeadas com sucesso.
------------------------------------------------------------
📂 Iniciando varredura em: /home/user/submissoes
🚀 Enviando A-Python3-equipe01.py...
   ✅ Sucesso!
🚀 Enviando B-Java-time02.java...
   ✅ Sucesso!
⚠️  Arquivo C-Rust-equipe03.rs: Linguagem 'Rust' não suportada. Pulei.
------------------------------------------------------------
🏁 Finalizado. 2 submissões processadas.
```
