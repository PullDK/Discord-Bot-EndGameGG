import discord
from discord import app_commands
from DataBase.pontos import carregar_dados, salvar_dados
from config.config_cargos import atribuir_cargo  # Importando atribuir_cargo
from .notificar import enviar_notificacao  # Importando a função para enviar notificações

def adicionar_pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='adicionar_pontos',
        description='Adiciona uma quantidade específica de pontos para um usuário mencionado'
    )
    @app_commands.describe(
        usuario="O usuário para quem você quer adicionar pontos",
        quantidade="A quantidade de pontos a adicionar",
        motivo="O motivo para a adição de pontos"
    )
    async def adicionar_pontos(interaction: discord.Interaction, usuario: discord.Member, quantidade: int, motivo: str):
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

        # Criação do embed
        embed = discord.Embed(
            title="Notificação de Adição de Pontos",
            color=discord.Color.green()  # Cor do embed
        )
        embed.add_field(name="Pontos:", value=f"+{quantidade}", inline=False)
        embed.add_field(name="Usuario:", value=usuario.mention, inline=False)
        embed.add_field(name="Motivo:", value=motivo, inline=False)
        embed.add_field(name="Quem adicionou os pontos:", value=interaction.user.mention, inline=False)  # Adiciona o autor da ação

        # Enviar notificação para o canal configurado
        await enviar_notificacao(
            interaction.guild_id,
            interaction.client,
            embed  # Passa o embed em vez de uma string
        )

        await interaction.response.send_message(
            f"{quantidade} pontos foram adicionados para {usuario.mention}!",
            ephemeral=True
        )
