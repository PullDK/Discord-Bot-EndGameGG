import discord
from discord import app_commands
from commands.Adicionar_Pontos import adicionar_pontos
from commands.Remover_Pontos import remover_pontos
from commands.Cargos import cargos
from commands.Pontos import pontos
from commands.Regras import regras
from commands.Comandos import comandos
from commands.Editar_Regras import editar_regras
from commands.notificar import definir_notificacao, canal_notificacao
from commands.configurar_tempo import configurar_tempo
from commands.configurar_hora import configurar_hora
from commands.config import definir_configuracoes
from ApiKey import key, dc
import json
import os
from config.horas_em_call import HoraEmCall  # Importando a nova classe para monitoramento de horários
from config.monitoramento import VoiceMonitor  # Mantendo o arquivo de monitoramento

id_do_servidor = dc  # Coloque aqui o ID do seu servidor

# Função para carregar dados do arquivo JSON
# Função para carregar dados do arquivo JSON
def carregar_dados():
    if not os.path.exists("dados.json"):
        # Se o arquivo não existir, cria um novo com valores padrão
        with open("dados.json", "w") as f:
            json.dump({
                "pontos": {},
                "cargos": {},
                "canal_notificacao": {},
                "hora_especifica": "05:07"  # Valor padrão
            }, f, indent=4)
    with open("dados.json", "r") as f:
        return json.load(f)


# Inicializar dados do servidor
def inicializar_dados(dados):
    if str(id_do_servidor) not in dados['pontos']:
        dados['pontos'][str(id_do_servidor)] = 0

dados = carregar_dados()
inicializar_dados(dados)

class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.voice_states = True  # Ativar intents de estados de voz
        super().__init__(intents=intents)
        self.synced = False
        self.hora_monitor = HoraEmCall(self, id_do_servidor, canal_notificacao)  # Instancia a nova classe para monitoramento de horários
        self.voice_monitor = VoiceMonitor(self, id_do_servidor)  # Mantendo o monitoramento existente

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True
        print(f"Entramos como {self.user}.")
        print("Iniciando monitoramento de horários em chamadas...")
        await self.hora_monitor.start_monitoring()  # Inicia o monitoramento de horários em chamadas
        await self.voice_monitor.start_monitoring()  # Inicia o monitoramento existente (se necessário)

aclient = Client()
tree = app_commands.CommandTree(aclient)

# Registrar comandos
pontos(tree, id_do_servidor)
adicionar_pontos(tree, id_do_servidor)
remover_pontos(tree, id_do_servidor)
cargos(tree, id_do_servidor)
regras(tree, id_do_servidor)
editar_regras(tree, id_do_servidor)
comandos(tree, id_do_servidor)
definir_notificacao(tree, id_do_servidor)
configurar_tempo(tree, id_do_servidor)
configurar_hora(tree, id_do_servidor)
definir_configuracoes(tree, id_do_servidor)

aclient.run(key)
