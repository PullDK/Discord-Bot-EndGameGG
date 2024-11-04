import discord
from discord import app_commands
from DataBase.pontos import carregar_dados, salvar_dados
import re

def configurar_hora(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='horas',
        description='Configura uma hora específica no formato HH:MM e salva no dados.json'
    )
    @app_commands.describe(hora="A hora no formato HH:MM")
    async def horas(interaction: discord.Interaction, hora: str):
        # Valida o formato de hora HH:MM usando regex
        padrao_hora = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        if not re.match(padrao_hora, hora):
            await interaction.response.send_message("Formato inválido! Use o formato HH:MM (ex: 04:26).", ephemeral=True)
            return

        # Carrega os dados do arquivo JSON
        dados = carregar_dados()
        dados['hora_especifica'] = hora  # Armazena a hora em formato HH:MM
        salvar_dados(dados)  # Salva os dados no arquivo JSON

        # Confirmação para o usuário
        await interaction.response.send_message(f"A hora foi configurada para {hora}!", ephemeral=True)
