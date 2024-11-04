import discord
from discord import app_commands
from DataBase.pontos import carregar_dados, salvar_dados

def configurar_tempo(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='call',
        description='Configura o tempo em segundos que um usuário deve ficar em call para ganhar pontos.'
    )
    @app_commands.describe(tempo="Tempo em segundos")
    async def call(interaction: discord.Interaction, tempo: int):
        dados = carregar_dados()
        dados['tempo_em_call'] = tempo  # Armazena o tempo em segundos
        salvar_dados(dados)  # Salva os dados no arquivo JSON

        await interaction.response.send_message(f"O tempo em call foi configurado para {tempo} segundos!", ephemeral=True)
