import discord
from discord import app_commands
from db.Sqlite import salvar_pontos, carregar_pontos, carregar_cargos  # Ajuste a importação conforme necessário

def adicionar_pontos(tree, id_do_servidor):
    @tree.command(
        guild=discord.Object(id=id_do_servidor),
        name='adicionar_pontos',
        description='Adiciona pontos a um usuário mencionado.'
    )
    @app_commands.describe(
        usuario="O usuário que você deseja adicionar pontos.",
        pontos="A quantidade de pontos a adicionar."
    )
    async def adicionar_pontos(interaction: discord.Interaction, usuario: discord.Member, pontos: int):
        user_id = str(usuario.id)  # Converte o ID do usuário para string
        pontos_atual = carregar_pontos().get(user_id, 0)  # Busca pontos atuais, padrão 0 se não encontrado
        
        # Atualiza os pontos
        novos_pontos = pontos_atual + pontos
        salvar_pontos(user_id, novos_pontos)
        
        # Carregar cargos
        cargos = carregar_cargos()  # Carregar os cargos do banco de dados
        mensagem = f"{pontos} pontos adicionados a {usuario.mention}. Total agora: {novos_pontos}."

        # Verifica e atribui o cargo correto
        cargo_adicionado = None
        for cargo_id, requisitos in cargos.items():
            if requisitos['min'] <= novos_pontos <= requisitos['max']:
                cargo = interaction.guild.get_role(cargo_id)
                if cargo and cargo not in usuario.roles:
                    await usuario.add_roles(cargo)  # Atribuir o cargo
                    cargo_adicionado = cargo.name  # Guarda o nome do cargo adicionado
                    mensagem += f" {usuario.mention} agora recebeu o cargo: {cargo.name}."
        
        # Remove cargos inferiores se necessário
        for cargo_id, requisitos in cargos.items():
            if requisitos['max'] < novos_pontos:  # Se o novo total de pontos é maior que o máximo do cargo
                cargo = interaction.guild.get_role(cargo_id)
                if cargo and cargo in usuario.roles:
                    await usuario.remove_roles(cargo)  # Remove o cargo inferior
                    mensagem += f" {usuario.mention} perdeu o cargo: {cargo.name}."
        
        # Envie a mensagem final
        await interaction.response.send_message(mensagem, ephemeral=True)
