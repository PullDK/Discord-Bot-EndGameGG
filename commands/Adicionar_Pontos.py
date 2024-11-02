import discord
from discord import app_commands
from db.MySql import carregar_pontos, salvar_pontos
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
        user_id = str(usuario.id)
        
        # Carregar pontos atuais do usuário
        pontos_atuais = carregar_pontos(user_id) or 0  # Se não houver registro, começa com 0
        
        # Adiciona os pontos ao usuário
        pontos_novos = pontos_atuais + quantidade
        salvar_pontos(user_id, pontos_novos)  # Salva os dados no MySQL
        
        # Atribui cargo automaticamente após adicionar pontos
        await atribuir_cargo(usuario)  # Certifique-se de chamar isso

        await interaction.response.send_message(
            f"{quantidade} pontos foram adicionados para {usuario.mention}!",
            ephemeral=True
        )
