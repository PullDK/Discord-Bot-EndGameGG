import discord
from discord import app_commands
import json
import os

# Função para carregar dados do arquivo JSON
def carregar_dados():
    if not os.path.exists("dados.json"):
        # Se o arquivo não existir, cria um novo com valores padrão
        with open("dados.json", "w") as f:
            json.dump({
                "pontos": {},
                "cargos": {},
                "canal_notificacao": {},
                "hora_especifica": "05:07",
                "tempo_em_call": 0,
                "regras": {}
            }, f, indent=4)
    with open("dados.json", "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)

def definir_configuracoes(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='configuracoes',
        description='Mostra as configurações atuais do bot.'
    )
    async def configuracoes(interaction: discord.Interaction):
        dados = carregar_dados()

        pontos = dados.get("pontos", {})
        cargos = dados.get("cargos", {})
        canal_notificacao = dados.get("canal_notificacao", {})
        tempo_em_call = dados.get("tempo_em_call", 0)
        hora_especifica = dados.get("hora_especifica", "N/A")

        # Criar uma embed para as informações
        embed = discord.Embed(
            title="Configurações Atuais",
            color=discord.Color.blue()
        )

        # Adicionando pontos
        embed.add_field(name="Pontos", value="\n".join([f"<@{user_id}>: {pontos_usuario} pontos" for user_id, pontos_usuario in pontos.items()]), inline=False)

        # Adicionando cargos
        cargos_info = "\n".join([f"Cargo ID: <@&{cargo_id}> (Min: {info['min']}, Max: {info['max']})" for cargo_id, info in cargos.items()])
        embed.add_field(name="Cargos", value=cargos_info or "Nenhum cargo configurado.", inline=False)

        # Adicionando canal de notificação
        canal_id = canal_notificacao.get(str(id_do_servidor), "Nenhum canal configurado.")
        embed.add_field(name="Canal de Notificação", value=f"<#{canal_id}>" if canal_id != "Nenhum canal configurado." else canal_id, inline=False)

        # Adicionando tempo em call e hora específica
        embed.add_field(name="Tempo em Call", value=f"{tempo_em_call} segundos", inline=False)
        embed.add_field(name="Hora Específica", value=hora_especifica, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='configuracoes_all',
        description='Adiciona dados que estão faltando no arquivo de configurações.'
    )
    async def configuracoes_all(interaction: discord.Interaction):
        dados = carregar_dados()
        dados_modificados = False
        
        # Verifica e adiciona dados padrão se estiverem faltando
        if "pontos" not in dados:
            dados["pontos"] = {}
            dados_modificados = True
        if "cargos" not in dados:
            dados["cargos"] = {}
            dados_modificados = True
        if "regras" not in dados:
            dados["regras"] = {}
            dados_modificados = True
        if "canal_notificacao" not in dados:
            dados["canal_notificacao"] = {}
            dados_modificados = True
        if "tempo_em_call" not in dados:
            dados["tempo_em_call"] = 14400
            dados_modificados = True
        if "hora_especifica" not in dados:
            dados["hora_especifica"] = "04:00"
            dados_modificados = True

        # Se algo foi modificado, salva as alterações no arquivo
        if dados_modificados:
            salvar_dados(dados)

        # Responder com a confirmação de que os dados foram verificados e, se necessário, adicionados
        await interaction.response.send_message("Todos os dados necessários foram verificados e preenchidos conforme necessário.", ephemeral=True)

# Adicionar a função de configurações ao seu bot
