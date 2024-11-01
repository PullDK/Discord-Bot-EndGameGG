# Comandos/addp.py
import discord
from discord import app_commands
from db.pontos import carregar_dados, salvar_dados
from config.config_cargos import atribuir_cargo  # Importando atribuir_cargo

def adicionar_pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='adicionar_pontos',
        description='Adiciona uma quantidade específica de pontos para um usuário mencionado'
    )
    @app_commands.describe(
        usuario="O usuário para quem você quer adicionar pontos",
        quantidade="A quantidade de pontos a adicionar"
    )
    async def adicionar_pontos(interaction: discord.Interaction, usuario: discord.Member, quantidade: int):
        dados = carregar_dados()
        user_id = str(usuario.id)

        # Adiciona os pontos ao usuário
        if user_id in dados["pontos"]:
            dados["pontos"][user_id] += quantidade
        else:
            dados["pontos"][user_id] = quantidade
        
        salvar_dados(dados)  # Salva os dados no arquivo JSON

        # Atribui cargo automaticamente após adicionar pontos
        await atribuir_cargo(usuario)  # Certifique-se de chamar isso

        await interaction.response.send_message(
            f"{quantidade} pontos foram adicionados para {usuario.mention}!",
            ephemeral=True
        )