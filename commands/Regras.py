import discord
from discord import app_commands
from db.Sqlite import carregar_regras, salvar_regras  # Atualizado para usar SQLite

def regras(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='regras',
        description='Gerencia as regras para ganhar ou perder pontos.'
    )
    async def regras_command(interaction: discord.Interaction, acao: str = None, tipo: str = None, pontos: str = None, *, descricao: str = None):
        print(f"Ação: {acao}, Tipo: {tipo}, Pontos: {pontos}, Descrição: {descricao}")  # Mensagem de depuração

        # Carrega as regras do banco de dados
        dados = carregar_regras()
        print(f"Dados carregados: {dados}")  # Verifique o que foi carregado

        # Inicializa as regras se não existirem
        if "regras" not in dados:
            dados["regras"] = {"ganhar": {}, "perder": {}}
        
        # Certifique-se de que a estrutura correta existe
        if not dados["regras"].get("ganhar"):
            dados["regras"]["ganhar"] = {}
        if not dados["regras"].get("perder"):
            dados["regras"]["perder"] = {}

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
            # Verifica se todos os parâmetros foram fornecidos
            if tipo is None or pontos is None or descricao is None:
                await interaction.response.send_message("Você precisa fornecer o tipo (ganhar/perder), pontos e uma descrição para adicionar uma regra.", ephemeral=True)
                return

            try:
                pontos = int(pontos)  # Conversão para inteiro
            except ValueError:
                await interaction.response.send_message("Os pontos devem ser um número válido.", ephemeral=True)
                return

            # Determina a categoria da regra (ganhar ou perder)
            if tipo.lower() == "ganhar":
                categoria = "ganhar"
            elif tipo.lower() == "perder":
                categoria = "perder"
            else:
                await interaction.response.send_message("Tipo inválido. Use 'ganhar' ou 'perder'.", ephemeral=True)
                return

            # Gera um ID único para a nova regra
            regra_id = str(len(dados["regras"][categoria]) + 1)  # Mantenha o ID como string

            # Adiciona a nova regra ao dicionário
            dados["regras"][categoria][regra_id] = {
                "tipo": tipo,
                "pontos": pontos,
                "descricao": descricao
            }

            # Salva as regras no banco de dados
            salvar_regras(dados["regras"])

            # Recarrega as regras para verificar se foram salvas
            dados = carregar_regras()
            print(f"Dados após salvar: {dados}")  # Verifique se os dados foram salvos corretamente

            await interaction.response.send_message("Regra adicionada com sucesso!", ephemeral=True)

        # Remover regra
        elif acao.lower() == "remover":
            # Verifica se todos os parâmetros foram fornecidos
            if tipo is None or pontos is None or descricao is None:
                await interaction.response.send_message("Você precisa fornecer o tipo (ganhar/perder), pontos e uma descrição para remover uma regra.", ephemeral=True)
                return

            # Determina a categoria da regra (ganhar ou perder)
            if tipo.lower() == "ganhar":
                categoria = "ganhar"
            elif tipo.lower() == "perder":
                categoria = "perder"
            else:
                await interaction.response.send_message("Tipo inválido. Use 'ganhar' ou 'perder'.", ephemeral=True)
                return

            if categoria not in dados["regras"] or not dados["regras"][categoria]:
                await interaction.response.send_message("Não existem regras cadastradas para esse tipo.", ephemeral=True)
                return

            # Encontra e remove a regra
            for regra_id, regra in list(dados["regras"][categoria].items()):
                if regra["descricao"] == descricao and regra["pontos"] == pontos:
                    del dados["regras"][categoria][regra_id]
                    salvar_regras(dados["regras"])
                    await interaction.response.send_message("Regra removida com sucesso!", ephemeral=True)
                    return

            await interaction.response.send_message("Regra não encontrada.", ephemeral=True)

    return regras_command
