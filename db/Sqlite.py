import sqlite3
import os

# Caminho do banco de dados SQLite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'DataBase', 'Pontos.sqlite')

def conectar():
    """Conecta ao banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def criar_tabelas():
    """Cria as tabelas necessárias no banco de dados se não existirem."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            
            # Criação da tabela de regras
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS regras (
                id_regra INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                pontos INTEGER NOT NULL,
                descricao TEXT NOT NULL
            )
            """)
            
            # Criação da tabela de usuários
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id TEXT PRIMARY KEY,
                pontos INTEGER NOT NULL
            )
            """)
            
            # Criação da tabela de cargos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cargos (
                cargo_id INTEGER PRIMARY KEY,
                min_pontos INTEGER NOT NULL,
                max_pontos INTEGER NOT NULL
            )
            """)
            
            conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")

def carregar_cargos():
    """Carrega todos os cargos e seus requisitos de pontos do banco de dados."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cargo_id, min_pontos, max_pontos FROM cargos")
            cargos = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao carregar cargos: {e}")
        return {}
    
    return {cargo_id: {"min": min_pontos, "max": max_pontos} for cargo_id, min_pontos, max_pontos in cargos}

def salvar_cargos(dados_cargos):
    """Salva ou atualiza os cargos no banco de dados com base nos dados fornecidos."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            
            for cargo_id, pontos in dados_cargos.items():
                min_pontos = pontos.get("min")
                max_pontos = pontos.get("max")
                
                # Atualiza ou insere o cargo no banco de dados
                cursor.execute(
                    """
                    INSERT INTO cargos (cargo_id, min_pontos, max_pontos) 
                    VALUES (?, ?, ?) 
                    ON CONFLICT(cargo_id) DO UPDATE SET 
                        min_pontos = excluded.min_pontos, 
                        max_pontos = excluded.max_pontos
                    """,
                    (cargo_id, min_pontos, max_pontos)
                )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao salvar cargos: {e}")

def carregar_pontos():
    """Carrega os pontos de todos os usuários do banco de dados."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, pontos FROM usuarios")
            pontos = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao carregar pontos: {e}")
        return {}
    
    return {str(user_id): pontos for user_id, pontos in pontos}

def salvar_pontos(user_id, pontos):
    """Salva os pontos de um usuário no banco de dados."""
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO usuarios (user_id, pontos) 
                VALUES (?, ?) 
                ON CONFLICT(user_id) DO UPDATE SET 
                    pontos = excluded.pontos
                """,
                (user_id, pontos)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao salvar pontos: {e}")

def carregar_regras():
    conn = None  # Inicializa conn como None
    try:
        conn = sqlite3.connect('DataBase/Pontos.sqlite')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM regras")
        regras = cursor.fetchall()

        dados = {"regras": {"ganhar": {}, "perder": {}}}
        for id_regra, tipo, pontos, descricao in regras:
            if tipo == "ganhar":
                dados["regras"]["ganhar"][id_regra] = {"tipo": tipo, "pontos": pontos, "descricao": descricao}
            elif tipo == "perder":
                dados["regras"]["perder"][id_regra] = {"tipo": tipo, "pontos": pontos, "descricao": descricao}
        
        return dados

    except Exception as e:
        print(f"Erro ao carregar regras: {e}")
        return {"regras": {"ganhar": {}, "perder": {}}}
    finally:
        if conn:
            conn.close()  # Fecha a conexão apenas se estiver definida



def salvar_regras(regras):
    try:
        conn = sqlite3.connect('DataBase/Pontos.sqlite')
        cursor = conn.cursor()

        # Limpa a tabela antes de salvar as novas regras
        cursor.execute("DELETE FROM regras")

        # Salva as novas regras no banco de dados
        for tipo, regras_dict in regras.items():
            for id_regra, regra in regras_dict.items():
                cursor.execute("INSERT INTO regras (id_regra, tipo, pontos, descricao) VALUES (?, ?, ?, ?)",
                               (id_regra, regra["tipo"], regra["pontos"], regra["descricao"]))

        conn.commit()
    except Exception as e:
        print(f"Erro ao salvar regras: {e}")
    finally:
        conn.close()

