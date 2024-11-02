import discord
from discord import app_commands
from db.MySql import carregar_regras, salvar_regras

def regras(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='regras',
        description='Gerencia as regras para ganhar ou perder pontos.'
    )
    async def regras_command(interaction: discord.Interaction, acao: str = None, tipo: str = None, pontos: str = None, *, descricao: str = None):
        # Carrega as regras do banco de dados
        dados = carregar_regras()

        # Inicializa as regras se não existirem
        if "regras" not in dados:
            dados["regras"] = {"ganhar": {}, "perder": {}}

        # Mostrar todas as regras se o comando for usado sem parâmetros
        if acao is None:
            embed = discord.Embed(title="Regras de Pontos", color=discord.Color.blue())
            
            # Verifica se existem regras
            if not dados.get("regras", {}).get("ganhar") and not dados.get("regras", {}).get("perder"):
                await interaction.response.send_message("Nenhuma regra encontrada.", ephemeral=True)
                return
            
            # Adiciona regras de ganhar pontos
            ganhando = "\n".join([f"{regra['descricao']} (+{regra['pontos']} pontos)" for regra in dados["regras"]["ganhar"].values()]) or "Nenhuma regra encontrada."
            embed.add_field(name="Ganhar Pontos", value=ganhando, inline=False)

            # Adiciona regras de perder pontos
            perdendo = "\n".join([f"{regra['descricao']} (-{regra['pontos']} pontos)" for regra in dados["regras"]["perder"].values()]) or "Nenhuma regra encontrada."
            embed.add_field(name="Perder Pontos", value=perdendo, inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


        # Adicionar regra
        if acao.lower() == "adicionar":
            if tipo is None or pontos is None or descricao is None:
                await interaction.response.send_message("Você precisa fornecer o tipo (ganhar/perder), pontos e uma descrição para adicionar uma regra.", ephemeral=True)
                return
            
            try:
                pontos = int(pontos)
            except ValueError:
                await interaction.response.send_message("Os pontos devem ser um número válido.", ephemeral=True)
                return

            # Determina a categoria da regra (ganhar ou perder)
            categoria = "ganhar" if tipo.lower() == "ganhar" else "perder" if tipo.lower() == "perder" else None
            
            if categoria is None:
                await interaction.response.send_message("Tipo inválido. Use 'ganhar' ou 'perder'.", ephemeral=True)
                return
            
            # Gera um ID único para a nova regra
            regra_id = str(len(dados["regras"][categoria]) + 1)  # Mantenha o ID como string
            dados["regras"][categoria][regra_id] = {"pontos": pontos, "descricao": descricao}

            salvar_regras(dados)  # Salva os dados no banco de dados
            await interaction.response.send_message(f"Regra adicionada: {descricao} ({'+' if categoria == 'ganhar' else ''}{pontos} pontos).", ephemeral=True)

        # Listar regras com IDs
        elif acao.lower() == "id":
            embed = discord.Embed(title="Regras", color=discord.Color.blue())

            # Adiciona regras de ganhar pontos
            for regra_id, regra in dados["regras"]["ganhar"].items():
                embed.add_field(name=f"ID {regra_id}: {regra['descricao']}", value=f"(+{regra['pontos']} pontos)", inline=False)

            # Adiciona regras de perder pontos
            for regra_id, regra in dados["regras"]["perder"].items():
                embed.add_field(name=f"ID {regra_id}: {regra['descricao']}", value=f"(-{regra['pontos']} pontos)", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        # Remover regra
        elif acao.lower() == "retirar":
            if tipo is None or pontos is None:
                await interaction.response.send_message("Você precisa fornecer o tipo (ganhar/perder) e o ID da regra que deseja remover.", ephemeral=True)
                return
            
            regra_id = str(pontos)  # Certifique-se de que o ID está como string

            # Determina a categoria da regra (ganhar ou perder)
            categoria = "ganhar" if tipo.lower() == "ganhar" else "perder" if tipo.lower() == "perder" else None
            
            if categoria is None:
                await interaction.response.send_message("Tipo inválido. Use 'ganhar' ou 'perder'.", ephemeral=True)
                return

            if regra_id in dados["regras"][categoria]:
                descricao = dados["regras"][categoria][regra_id]["descricao"]
                del dados["regras"][categoria][regra_id]  # Remove a regra
                salvar_regras(dados)  # Salva os dados no banco de dados
                await interaction.response.send_message(f"Regra removida: {descricao}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Regra com ID {regra_id} não encontrada na categoria '{tipo}'.", ephemeral=True)

        else:
            await interaction.response.send_message("Ação inválida. Use 'adicionar', 'id' ou 'retirar'.", ephemeral=True)
