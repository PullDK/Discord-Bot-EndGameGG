# Comandos/cargos.py
import discord
from db.pontos import carregar_dados

async def atribuir_cargo(usuario: discord.Member):
    dados = carregar_dados()
    pontos = dados["pontos"].get(str(usuario.id), 0)  # Obtém os pontos do usuário
    guild = usuario.guild  # Obtém o servidor do usuário

    # Remove todos os cargos que o usuário não pode mais manter
    for cargo_id, limites in dados["cargos"].items():
        cargo_role = guild.get_role(int(cargo_id))  # Obtém o cargo pelo ID
        # Se o usuário tem o cargo e não atende mais aos limites, remove
        if cargo_role in usuario.roles:
            if pontos < limites["min"] or (limites["max"] is not None and pontos > limites["max"]):
                await usuario.remove_roles(cargo_role)  # Remove se o usuário não atender aos limites

    # Atribui o cargo correspondente baseado nos pontos
    cargo_a_atribuir = None
    for cargo_id, limites in dados["cargos"].items():
        # Verifica se o usuário atende aos limites para o cargo
        if pontos >= limites["min"] and (limites["max"] is None or pontos <= limites["max"]):
            # Se já existir um cargo atribuído e o novo cargo for de menor valor, não atribua
            if cargo_a_atribuir is None or limites["min"] > dados["cargos"][cargo_a_atribuir]["min"]:
                cargo_a_atribuir = cargo_id  # Encontra o cargo que o usuário pode ter

    # Se o cargo a atribuir for diferente do que o usuário já tem
    if cargo_a_atribuir:
        cargo_role = guild.get_role(int(cargo_a_atribuir))  # Obtém o cargo pelo ID
        if cargo_role and cargo_role not in usuario.roles:
            await usuario.add_roles(cargo_role)  # Atribui o cargo se não estiver presente
