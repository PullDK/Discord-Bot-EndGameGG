# commands/comandos.py
import discord
from discord import app_commands

def comandos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='comandos',
        description='Mostra todos os comandos disponíveis e exemplos de uso.'
    )
    async def comandos_command(interaction: discord.Interaction):
        embed = discord.Embed(title="Comandos Disponíveis", color=discord.Color.blue())

        embed.add_field(name="Ver pontos de todos os usuários:", value="/pontos", inline=False)

        embed.add_field(name="Adicionar pontos:", value="/adicionar_pontos @usuário 10", inline=False)

        embed.add_field(name="Remover pontos:", value="/remover_pontos @usuário 5", inline=False)

        embed.add_field(name="Configurar qual cargo o usuário vai receber com uma certa quantidade de pontos:", value="/cargos @cargo {Quantidade mínima} {Quantidade máxima}", inline=False)

        embed.add_field(name="Ver todas as regras:", value="/regras", inline=False)
        embed.add_field(name="Adicionar uma nova regra para ganhar pontos:", value="/regras adicionar ganhar +10 elogiar amigo", inline=False)
        embed.add_field(name="Adicionar uma nova regra para perder pontos:", value="/regras adicionar perder -10 sair da call", inline=False)
        embed.add_field(name="Mostrar os IDs das regras:", value="/regras id", inline=False)
        embed.add_field(name="Remover a regra de ganhar pontos do ID 1:", value="/regras retirar ganhar 1", inline=False)
        embed.add_field(name="Remover a regra de perder pontos do ID 1:", value="/regras retirar perder 1", inline=False)
        embed.add_field(name="Editar as regras:", value="/editar_regras ganhar 1 novos_pontos: 7 nova_descricao: Ficar mais de 3 horas em call", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


