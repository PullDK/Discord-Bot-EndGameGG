import mysql.connector

# Conexão ao banco de dados
db = mysql.connector.connect(
    host="135.148.135.159",
    user="u302_tIa5YgTroQ",
    password=".VC^9aiSBaM6I^5dAa6YFTkX",
    database="s302_membros"
)
cursor = db.cursor()

# Função para criar a tabela de pontos se ela não existir
def criar_tabela_pontos():
    cursor.execute("""CREATE TABLE IF NOT EXISTS pontos (
        user_id VARCHAR(20) PRIMARY KEY,
        pontos INT
    );""")
    db.commit()

# Função para criar a tabela de regras se ela não existir
def criar_tabela_regras():
    cursor.execute("""CREATE TABLE IF NOT EXISTS regras (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tipo ENUM('ganhar', 'perder'),
        descricao VARCHAR(255),
        pontos INT
    );""")
    db.commit()

# Função para criar a tabela de cargos se ela não existir
def criar_tabela_cargos():
    cursor.execute("""CREATE TABLE IF NOT EXISTS cargos (
        cargo_id VARCHAR(20) PRIMARY KEY,
        min INT,
        max INT
    );""")
    db.commit()

# Função para carregar pontos
def carregar_pontos(user_id):
    criar_tabela_pontos()  # Garante que a tabela existe
    cursor.execute("SELECT pontos FROM pontos WHERE user_id = %s", (user_id,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

# Função para salvar pontos
def salvar_pontos(user_id, pontos):
    criar_tabela_pontos()  # Garante que a tabela existe
    cursor.execute("""INSERT INTO pontos (user_id, pontos) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE pontos = %s""", (user_id, pontos, pontos))
    db.commit()

# Função para carregar regras
def carregar_regras():
    criar_tabela_regras()  # Garante que a tabela existe
    cursor.execute("SELECT tipo, descricao, pontos FROM regras")
    regras = cursor.fetchall()
    dados = {"ganhar": {}, "perder": {}}
    
    for tipo, descricao, pontos in regras:
        # Armazena regras de acordo com o tipo
        dados[tipo][str(len(dados[tipo]) + 1)] = {"pontos": pontos, "descricao": descricao}
    
    return {"regras": dados}  # Adiciona 'regras' como chave principal

# Função para salvar regras
def salvar_regras(dados):
    criar_tabela_regras()  # Garante que a tabela existe
    cursor.execute("DELETE FROM regras")  # Limpa a tabela atual
    for tipo, regras in dados.items():
        for regra_id, regra in regras.items():
            cursor.execute(
                "INSERT INTO regras (tipo, descricao, pontos) VALUES (%s, %s, %s)",
                (tipo, regra['descricao'], regra['pontos'])
            )
    db.commit()

# Função para carregar cargos
def carregar_cargos():
    criar_tabela_cargos()  # Garante que a tabela existe
    cursor.execute("SELECT cargo_id, min, max FROM cargos")
    resultados = cursor.fetchall()
    
    cargos = {}
    for cargo_id, min_pontos, max_pontos in resultados:
        cargos[cargo_id] = {"min": min_pontos, "max": max_pontos}
    
    return cargos

# Função para salvar cargos
def salvar_cargos(dados):
    criar_tabela_cargos()  # Garante que a tabela existe
    cursor.execute("DELETE FROM cargos")  # Limpa a tabela atual
    for cargo_id, valores in dados.items():
        cursor.execute(
            "INSERT INTO cargos (cargo_id, min, max) VALUES (%s, %s, %s)",
            (cargo_id, valores['min'], valores['max'])
        )
    db.commit()

# Função para carregar todos os pontos
def carregar_todos_pontos():
    criar_tabela_pontos()  # Garante que a tabela existe
    cursor.execute("SELECT user_id, pontos FROM pontos")
    resultados = cursor.fetchall()
    
    pontos = {}
    for user_id, pontos_usuario in resultados:
        pontos[user_id] = pontos_usuario
    
    return pontos

# Função para fechar a conexão
def fechar_conexao():
    cursor.close()
    db.close()

# Exemplo de uso
if __name__ == "__main__":
    try:
        # Salvar alguns pontos
        salvar_pontos('123456789012345678', 50)

        # Carregar e exibir pontos de um usuário
        pontos_usuario = carregar_pontos('123456789012345678')
        print(f"Pontos do usuário: {pontos_usuario}")

        # Salvar regras
        regras = {
            "ganhar": {
                "1": {"pontos": 5, "descricao": "Ficar mais de 4 horas em call"},
                "2": {"pontos": 10, "descricao": "Ficar até às 4 da madrugada"}
            },
            "perder": {
                "1": {"pontos": 5, "descricao": "Mutar sem avisar"}
            }
        }
        salvar_regras(regras)

        # Salvar cargos
        cargos = {
            "1299627956230029344": {"min": 0, "max": 0},
            "1299627636238057525": {"min": 1, "max": 59}
        }
        salvar_cargos(cargos)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Fechar a conexão ao final
        fechar_conexao()
