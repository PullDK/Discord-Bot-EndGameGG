import discord
from discord import app_commands
from db.MySql import carregar_regras, salvar_regras  # Atualize a importação conforme sua estrutura

def editar_regras(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='editar_regras',
        description='Edita as regras de ganhar ou perder pontos.'
    )
    @app_commands.describe(
        tipo="O tipo da regra a ser editada (ganhar ou perder)",
        id_regra="O ID da regra a ser editada",
        novos_pontos="A nova quantidade de pontos",
        nova_descricao="A nova descrição da regra"
    )
    async def editar_regras(interaction: discord.Interaction, tipo: str, id_regra: str, novos_pontos: int, nova_descricao: str):
        # Carrega os dados
        dados = carregar_regras()
        
        # Verifica se o tipo da regra é válido
        if tipo not in dados:
            await interaction.response.send_message("Tipo de regra inválido! Use 'ganhar' ou 'perder'.", ephemeral=True)
            return
        
        # Verifica se o ID da regra existe
        if id_regra not in dados[tipo]:
            await interaction.response.send_message(f"ID da regra {id_regra} não encontrado em regras de {tipo}.", ephemeral=True)
            return
        
        # Atualiza os dados da regra
        dados[tipo][id_regra]["pontos"] = novos_pontos
        dados[tipo][id_regra]["descricao"] = nova_descricao
        
        # Salva os dados no banco de dados
        salvar_regras(dados)

        await interaction.response.send_message(f"Regra {id_regra} de {tipo} atualizada com sucesso!", ephemeral=True)
