# Comandos/cargos.py
import discord
from discord import app_commands
from db.Sqlite import carregar_cargos, salvar_cargos  # Atualizado para usar SQLite

def cargos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='cargos',
        description='Adiciona ou remove um cargo com uma quantidade de pontos'
    )
    @app_commands.describe(
        cargo="O cargo que você deseja adicionar ou remover",
        min_pontos="A quantidade mínima de pontos necessária para obter esse cargo (deixe em branco para remover o cargo)",
        max_pontos="A quantidade máxima de pontos para obter esse cargo (deixe em branco para remover o cargo)"
    )
    async def cargos(interaction: discord.Interaction, cargo: str, min_pontos: int = None, max_pontos: int = None):
        dados_cargos = carregar_cargos()  # Carrega os cargos do banco de dados

        # Salve apenas o ID do cargo sem a menção
        cargo_id = cargo.strip('<@&>')  # Remove '<@&' e '>'

        if min_pontos is None and max_pontos is None:
            # Se não foram fornecidos min e max, remove o cargo do banco de dados
            if cargo_id in dados_cargos:
                del dados_cargos[cargo_id]  # Remove o cargo
                resposta = f"O cargo '<@&{cargo_id}>' foi removido!"
            else:
                resposta = f"O cargo '<@&{cargo_id}>' não existe!"
        else:
            # Se os pontos mínimos ou máximos foram fornecidos, adiciona ou atualiza o cargo
            dados_cargos[cargo_id] = {"min": min_pontos, "max": max_pontos}
            resposta = f"O cargo '<@&{cargo_id}>' agora requer entre {min_pontos} e {max_pontos} pontos!"

        salvar_cargos(dados_cargos)  # Salva os dados no banco de dados
        await interaction.response.send_message(resposta, ephemeral=True)
