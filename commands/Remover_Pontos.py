# Comandos/removerp.py
import discord
from discord import app_commands
from db.pontos import carregar_dados, salvar_dados
from config.config_cargos import atribuir_cargo  # Importando atribuir_cargo

def remover_pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='remover_pontos',
        description='Remove uma quantidade específica de pontos de um usuário mencionado'
    )
    @app_commands.describe(
        usuario="O usuário do qual você quer remover pontos",
        quantidade="A quantidade de pontos a remover"
    )
    async def remover_pontos(interaction: discord.Interaction, usuario: discord.Member, quantidade: int):
        dados = carregar_dados()
        user_id = str(usuario.id)

        # Verifica se o usuário tem pontos registrados e subtrai
        if user_id in dados["pontos"]:
            dados["pontos"][user_id] = max(0, dados["pontos"][user_id] - quantidade)  # Garante que o valor não fique negativo
        else:
            dados["pontos"][user_id] = 0  # Usuário não tinha pontos, então permanece com 0

        salvar_dados(dados)  # Salva os dados no arquivo JSON

        # Atribui cargo automaticamente após remover pontos
        await atribuir_cargo(usuario)

        await interaction.response.send_message(
            f"{quantidade} pontos foram removidos de {usuario.mention}!",
            ephemeral=True
        )
