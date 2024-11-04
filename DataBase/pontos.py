import json
import os

def carregar_dados():
    # Verifica se o arquivo existe
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            try:
                # Tenta carregar os dados do arquivo JSON
                return json.load(f)
            except json.JSONDecodeError:
                # Retorna um dicionário padrão se houver um erro na leitura do JSON
                return {"pontos": {}, "cargos": {}, "regras": {"ganhar": {}, "perder": {}}}

    # Se o arquivo não existir, retorna um dicionário padrão
    return {"pontos": {}, "cargos": {}, "regras": {"ganhar": {}, "perder": {}}}

def salvar_dados(dados):
    # Salva os dados no arquivo JSON
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)
