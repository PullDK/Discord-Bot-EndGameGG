import discord
from discord import app_commands
import json
import os

# Dicionário em memória para armazenar o canal de notificação
canal_notificacao = {}

# Função para carregar os dados do arquivo JSON
def carregar_dados():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            return json.load(f)
    return {"canal_notificacao": {}}

# Função para salvar os dados no arquivo JSON
def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

# Carrega os dados ao iniciar o script
dados = carregar_dados()
canal_notificacao = dados.get("canal_notificacao", {})

def definir_notificacao(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='notificar',
        description='Define o canal para notificações de pontos'
    )
    @app_commands.describe(
        canal="O canal onde as notificações serão enviadas"
    )
    async def notificar(interaction: discord.Interaction, canal: discord.TextChannel):
        # Define o canal para o servidor
        canal_notificacao[id_do_servidor] = canal.id

        # Atualiza o JSON com o novo canal de notificação
        dados["canal_notificacao"] = canal_notificacao
        salvar_dados(dados)

        await interaction.response.send_message(
            f"As notificações de pontos serão enviadas no canal {canal.mention}.",
            ephemeral=True
        )

async def enviar_notificacao(id_do_servidor, bot, mensagem):
    # Converte o ID do servidor para string
    server_id_str = str(id_do_servidor)
    
    # Verifica se há um canal configurado para o servidor
    if server_id_str in canal_notificacao:
        canal_id = canal_notificacao[server_id_str]
        canal = bot.get_channel(canal_id)
        
        if canal:
            if isinstance(mensagem, discord.Embed):  # Verifica se a mensagem é um embed
                await canal.send(embed=mensagem)  # Envia o embed
            else:
                await canal.send(mensagem)  # Envia a mensagem de texto
        else:
            print(f"Erro: Canal com ID {canal_id} não encontrado no servidor {id_do_servidor}.")
    else:
        print(f"Nenhum canal de notificação configurado para o servidor {id_do_servidor}.")

