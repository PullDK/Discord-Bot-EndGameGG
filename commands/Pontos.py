import discord
from discord import app_commands
from db.MySql import carregar_todos_pontos, carregar_cargos  # Use a nova função

def pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='pontos',
        description='Mostra todos os usuários e seus pontos com os respectivos cargos.'
    )
    async def pontos_command(interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title="Usuários e Cargos", color=discord.Color.blue())

        # Carrega todos os pontos e cargos do banco de dados
        dados_pontos = carregar_todos_pontos()  # Use a nova função
        dados_cargos = carregar_cargos()

        if not dados_pontos:
            embed.description = "Nenhum usuário encontrado.\nNão há usuários com pontos registrados."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        for user_id, pontos in dados_pontos.items():
            user = guild.get_member(int(user_id))
            if user is not None:
                cargo_atual = "Nenhum cargo"
                # Verifica os cargos correspondentes
                for cargo_id, limites in dados_cargos.items():
                    if limites["min"] <= pontos <= limites["max"]:
                        cargo_atual = guild.get_role(int(cargo_id))
                        break
                
                # Adiciona o cargo e o usuário na embed
                embed.add_field(name=str(cargo_atual), value=f"{user.mention}: {pontos} pontos", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
