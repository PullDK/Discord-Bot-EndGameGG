import discord
from discord import app_commands
from commands.Adicionar_Pontos import adicionar_pontos
from commands.Remover_Pontos import remover_pontos
from commands.Cargos import cargos
from commands.Pontos import pontos
from commands.Regras import regras
from commands.Comandos import comandos
from commands.Editar_Regras import editar_regras
from ApiKey import key, dc
from db.Sqlite import criar_tabelas
import json
import os

id_do_servidor = dc

def inicializar_dados():
    # Cria o arquivo com dados padrão se ele não existir
    if not os.path.exists("dados.json"):
        with open("dados.json", "w") as f:
            json.dump({"pontos": {}, "cargos": {}}, f, indent=4)

class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # Habilita a intenção de membros
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True
        
        # Atualiza a presença do bot
        await self.change_presence(activity=discord.Game(name="Minecraft 2"))
        
        print(f"Entramos como {self.user}.")

aclient = Client()
tree = app_commands.CommandTree(aclient)

# Inicializa os dados antes de registrar comandos
inicializar_dados()
criar_tabelas()

# Registra os comandos
pontos(tree, id_do_servidor)
adicionar_pontos(tree, id_do_servidor)
remover_pontos(tree, id_do_servidor)
cargos(tree, id_do_servidor)
regras(tree, id_do_servidor)
editar_regras(tree, id_do_servidor)
comandos(tree, id_do_servidor)

aclient.run(key)
