import pandas as pd
import json

caminho_arquivo = 'c:/projects/tcc_api/scripts/transform-json-into-csv/B/c_cpp'
# Nome do seu arquivo JSON de entrada
json_filename = f'{caminho_arquivo}/response_1762612697728.json'
# Nome do arquivo CSV de saída
csv_filename = f'{caminho_arquivo}/output_results.csv'

try:
    # 1. Carregar o arquivo JSON
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Acessar a lista 'results' e criar um DataFrame
    # O Pandas converte a lista de dicionários diretamente para uma tabela
    df = pd.DataFrame(data['results'])

    # 3. Salvar o DataFrame em um arquivo CSV
    # index=False evita que o Pandas adicione uma coluna extra de índice (0, 1, 2...)
    df.to_csv(csv_filename, index=False, encoding='utf-8')

    print(f"Arquivo '{csv_filename}' criado com sucesso!")

except FileNotFoundError:
    print(f"Erro: O arquivo '{json_filename}' não foi encontrado.")
except KeyError:
    print("Erro: A chave 'results' não foi encontrada no JSON.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")