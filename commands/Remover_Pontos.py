# Comandos/removerp.py
import discord
from discord import app_commands
from db.MySql import carregar_pontos, salvar_pontos
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
        user_id = str(usuario.id)

        # Carrega os pontos atuais do usuário, ou começa com 0 se não houver registro
        pontos_atuais = carregar_pontos(user_id) or 0

        # Subtrai a quantidade, garantindo que o total não fique negativo
        novos_pontos = max(0, pontos_atuais - quantidade)
        
        # Salva o novo valor de pontos no banco de dados
        salvar_pontos(user_id, novos_pontos)

        # Atribui cargo automaticamente após remover pontos
        await atribuir_cargo(usuario)

        await interaction.response.send_message(
            f"{quantidade} pontos foram removidos de {usuario.mention}!",
            ephemeral=True
        )
