import discord
from discord import app_commands
from db.Sqlite import salvar_pontos, carregar_pontos, carregar_cargos  # Ajuste a importação conforme necessário

def remover_pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='remover_pontos',
        description='Remove pontos de um usuário mencionado.'
    )
    @app_commands.describe(
        usuario="O usuário que você deseja remover pontos.",
        pontos="A quantidade de pontos a remover."
    )
    async def remover_pontos_command(interaction: discord.Interaction, usuario: discord.Member, pontos: int):
        user_id = str(usuario.id)  # Converte o ID do usuário para string
        pontos_atuais = carregar_pontos().get(user_id, 0)  # Busca pontos atuais, padrão 0 se não encontrado
        
        # Verifica se há pontos suficientes para remover
        if pontos_atuais < pontos:
            await interaction.response.send_message(f"{usuario.mention} não tem pontos suficientes para remover!", ephemeral=True)
            return
        
        # Atualiza os pontos
        novos_pontos = pontos_atuais - pontos
        salvar_pontos(user_id, novos_pontos)
        
        # Carregar cargos e verificar se é necessário remover algum cargo
        cargos = carregar_cargos()  # Carrega os cargos do banco de dados
        cargo_removido = None
        
        # Verifica se o usuário precisa perder algum cargo
        for cargo_id, requisitos in cargos.items():
            if novos_pontos < requisitos['min'] or novos_pontos > requisitos['max']:
                cargo = interaction.guild.get_role(cargo_id)
                if cargo in usuario.roles:
                    await usuario.remove_roles(cargo)  # Remove o cargo
                    cargo_removido = cargo.name  # Guarda o nome do cargo removido
                    break  # Para remover apenas um cargo que não se aplica mais

        # Mensagem de resposta
        mensagem = f"{pontos} pontos removidos de {usuario.mention}. Total agora: {novos_pontos}."
        if cargo_removido:
            mensagem += f" {usuario.mention} perdeu o cargo: {cargo_removido}."
        
        await interaction.response.send_message(mensagem, ephemeral=True)

