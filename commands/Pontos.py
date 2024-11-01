# commands/pontos.py
import discord
from discord import app_commands
from db.pontos import carregar_dados

def pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='pontos',
        description='Mostra todos os usuários e seus pontos com os respectivos cargos.'
    )
    async def pontos_command(interaction: discord.Interaction):
        dados = carregar_dados()
        guild = interaction.guild
        embed = discord.Embed(title="Usuários e Cargos", color=discord.Color.blue())
        
        if not dados["pontos"]:
            embed.description = "Nenhum usuário encontrado.\nNão há usuários com pontos registrados."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        for user_id, pontos in dados["pontos"].items():
            user = guild.get_member(int(user_id))
            if user is not None:
                cargo_atual = "Nenhum cargo"
                # Verifica os cargos correspondentes
                for cargo_id, limites in dados["cargos"].items():
                    if limites["min"] <= pontos <= limites["max"]:
                        cargo_atual = guild.get_role(int(cargo_id))
                        break
                
                # Adiciona o cargo e o usuário na embed
                embed.add_field(name=str(cargo_atual), value=f"{user.mention}: pontos {pontos}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
