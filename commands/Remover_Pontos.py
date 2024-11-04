import discord
from discord import app_commands
from DataBase.pontos import carregar_dados, salvar_dados
from config.config_cargos import atribuir_cargo  # Importando atribuir_cargo
from .notificar import enviar_notificacao  # Importando a função para enviar notificações

def remover_pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='remover_pontos',
        description='Remove uma quantidade específica de pontos de um usuário mencionado'
    )
    @app_commands.describe(
        usuario="O usuário do qual você quer remover pontos",
        quantidade="A quantidade de pontos a remover",
        motivo="O motivo para a remoção de pontos"
    )
    async def remover_pontos(interaction: discord.Interaction, usuario: discord.Member, quantidade: int, motivo: str):
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

        # Criação do embed
        embed = discord.Embed(
            title="Notificação de Remoção de Pontos",
            color=discord.Color.red()  # Cor do embed
        )
        embed.add_field(name="Pontos:", value=f"-{quantidade}", inline=False)
        embed.add_field(name="Usuario:", value=usuario.mention, inline=False)
        embed.add_field(name="Motivo:", value=motivo, inline=False)
        embed.add_field(name="Quem retirou os pontos:", value=interaction.user.mention, inline=False)

        # Enviar notificação para o canal configurado
        await enviar_notificacao(
            interaction.guild_id,
            interaction.client,
            embed  # Passa o embed em vez de uma string
        )

        await interaction.response.send_message(
            f"{quantidade} pontos foram removidos de {usuario.mention}!",
            ephemeral=True
        )
