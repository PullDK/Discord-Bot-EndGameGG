import discord
from discord.ext import commands
import json
import time
import os

from apikey import *

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True  # Habilitar eventos de estado de voz

client = commands.Bot(command_prefix='!', intents=intents)

# Caminho do arquivo de dados
data_file = "data.json"

def load_data():
    if not os.path.exists(data_file):
        return {"points": {}, "roles": {}, "notify_channel": None}  # Adiciona notify_channel
    with open(data_file, "r") as file:
        return json.load(file)

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

# Dicionário para armazenar o tempo em chamada
user_voice_times = {}
# Dicionário para armazenar a configuração de pontos por tempo
points_per_time = {}

@client.event
async def on_ready():
    print('Bot já está em execução')

@client.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)

    if after.channel is not None:
        if user_id not in user_voice_times:
            user_voice_times[user_id] = time.time()
    else:
        if user_id in user_voice_times:
            duration = time.time() - user_voice_times[user_id]
            await update_points(member, duration)
            del user_voice_times[user_id]

async def update_points(member, duration):
    points = 0
    for time_limit, point_value in points_per_time.items():
        if duration >= time_limit:
            points += point_value

    if points > 0:
        await add_points(member, points)

async def add_points(member, points):
    data = load_data()
    user_id = str(member.id)

    if user_id not in data["points"]:
        data["points"][user_id] = 20

    data["points"][user_id] += points
    await assign_role(member, data["points"][user_id], data["roles"], data["notify_channel"])  # Passa o canal para notificação
    save_data(data)

@client.command()
async def horasp(ctx, seconds: int = None, points: int = None):
    if seconds is None or points is None:
        await ctx.send("Uso correto: `!horasp segundos pontos`")
        return

    points_per_time[seconds] = points
    await ctx.send(f'Configuração: {points} pontos para {seconds} segundos em call.')

@client.command()
async def addp(ctx, usuario: discord.Member = None, pontos: int = None):
    if usuario is None or pontos is None:
        await ctx.send("Uso correto: `!addp @usuario pontos`")
        return

    data = load_data()
    user_id = str(usuario.id)

    if user_id not in data["points"]:
        data["points"][user_id] = 20
    
    data["points"][user_id] += pontos
    await assign_role(usuario, data["points"][user_id], data["roles"], data["notify_channel"])  # Passa o canal para notificação
    save_data(data)
    await ctx.send(f'{pontos} pontos foram adicionados a {usuario.name}. Pontuação total: {data["points"][user_id]} pontos.')

@client.command()
async def remp(ctx, usuario: discord.Member, pontos: int):
    # Carrega os dados do arquivo data.json
    data = load_data()  # Use a função que já lida com a abertura do arquivo

    user_id = str(usuario.id)

    # Verifica se o usuário existe nos dados
    if user_id not in data["points"]:
        await ctx.send(f'O usuário {usuario.name} não possui pontos registrados.')
        return

    # Remove os pontos
    data["points"][user_id] -= pontos

    # Garante que os pontos não sejam negativos
    if data["points"][user_id] < 0:
        data["points"][user_id] = 0

    # Atualiza o arquivo data.json
    save_data(data)

    # Atualiza os cargos do usuário
    await assign_role(usuario, data["points"][user_id], data["roles"], data["notify_channel"])

    await ctx.send(f'{pontos} pontos foram removidos de {usuario.name}.')

@client.command()
async def allp(ctx):
    data = load_data()
    
    if not data["points"]:
        await ctx.send("Nenhum usuário registrado.")
        return

    # Organizar os usuários em um dicionário para armazenar seu cargo mais alto
    cargos = {}
    
    # Iterar sobre cada usuário e verificar qual é o seu cargo mais alto
    for user_id, pontos in data["points"].items():
        # Verificar os cargos disponíveis e se o usuário atende aos critérios de pontos
        for pontos_min, role_id in sorted(data["roles"].items(), key=lambda x: int(x[0]), reverse=True):
            if pontos >= int(pontos_min):
                # Se o usuário já tem um cargo atribuído, comparar para manter o de maior pontuação
                if user_id not in cargos or int(pontos_min) > cargos[user_id][0]:
                    cargos[user_id] = (int(pontos_min), role_id)  # Armazena pontos mínimos e o id do cargo
                break  # Para ao encontrar o primeiro cargo mais alto que atende aos pontos

    # Criar um dicionário para armazenar usuários por cargo
    usuarios_por_cargo = {}
    
    # Agrupar usuários por seus cargos
    for user_id, (pontos_min, role_id) in cargos.items():
        if role_id not in usuarios_por_cargo:
            usuarios_por_cargo[role_id] = []
        usuarios_por_cargo[role_id].append(user_id)

    # Criar o embed
    embed = discord.Embed(
        title="Pontuação dos Usuários",
        color=discord.Color.green()
    )

    # Adicionar campos ao embed para cada cargo, em ordem hierárquica
    for pontos_min, role_id in sorted(data["roles"].items(), key=lambda x: int(x[0]), reverse=True):
        if role_id in usuarios_por_cargo:  # Verifica se há usuários com esse cargo
            role = ctx.guild.get_role(int(role_id))  # Obtém o objeto do cargo
            if role:  # Verifica se o cargo existe
                role_name = role.name  # Obtém o nome do cargo
                usuarios_info = "\n".join([f"<@{user_id}>: {data['points'][user_id]} pontos" for user_id in usuarios_por_cargo[role_id]])
                embed.add_field(name=role_name, value=usuarios_info, inline=False)

    # Caso não haja cargos atribuídos a nenhum usuário
    if not usuarios_por_cargo:
        embed.description = "Nenhum cargo configurado com usuários."
    
    await ctx.send(embed=embed)

@client.command()
async def cargop(ctx, cargo: discord.Role = None, pontos: int = None):
    if cargo is None or pontos is None:
        await ctx.send("Uso correto: `!cargop @cargo pontos`")
        return

    data = load_data()

    # Verifica se já existe um cargo associado a uma quantidade de pontos
    for pontos_limite in list(data["roles"].keys()):
        # Se a quantidade de pontos já existir, remove
        if pontos_limite != str(pontos):  # Não remove se a quantidade for igual
            if data["roles"][pontos_limite] == cargo.id:  # Remove cargo atual
                del data["roles"][pontos_limite]
                break

    # Atualiza ou adiciona a nova configuração
    data["roles"][str(pontos)] = cargo.id
    save_data(data)
    await ctx.send(f'O cargo {cargo.name} foi atribuído a {pontos} pontos.')

import discord

@client.command()
async def cfgp(ctx):
    data = load_data()
    
    # Obtendo os cargos configurados
    roles_info = "\n".join([f"{pontos} pontos: <@&{role_id}>" for pontos, role_id in data["roles"].items()]) or "Nenhum cargo configurado."
    
    # Obtendo o canal de notificação
    notify_channel_info = f"<#{data['notify_channel']}>" if data["notify_channel"] else "Nenhum canal configurado."
    
    # Criando o embed
    embed = discord.Embed(
        title="Configurações do Bot",
        color=discord.Color.blue()  # Você pode escolher outra cor, se desejar
    )
    
    # Adicionando os campos de informações ao embed
    embed.add_field(name="Cargos Configurados", value=roles_info, inline=False)
    embed.add_field(name="Canal de Notificação", value=notify_channel_info, inline=False)
    
    # Enviando o embed como resposta
    await ctx.send(embed=embed)



@client.command()
async def canalr(ctx):
    data = load_data()
    data["notify_channel"] = None  # Remove o canal de notificação
    save_data(data)
    await ctx.send("O canal de notificação foi removido.")


@client.command()
async def cargor(ctx, cargo: discord.Role = None):
    if cargo is None:
        await ctx.send("Uso correto: `!cargor @cargo`")
        return

    data = load_data()
    role_removed = False  # Para verificar se o cargo foi removido

    # Itera sobre os cargos para encontrar e remover o cargo especificado
    for pontos_limite in list(data["roles"].keys()):
        if data["roles"][pontos_limite] == cargo.id:
            del data["roles"][pontos_limite]  # Remove o cargo
            role_removed = True
            break

    if role_removed:
        save_data(data)
        await ctx.send(f'O cargo {cargo.name} foi removido com sucesso.')
    else:
        await ctx.send(f'O cargo {cargo.name} não estava associado a nenhuma quantidade de pontos.')


import discord
from discord.ext import commands

@client.command()
async def cmdp(ctx):
    commands_info = [
        "!addp @usuario pontos - Adiciona pontos a um usuário.",
        "!remp @usuario pontos - Remove pontos de um usuário.",
        "!allp - Mostra todos os usuários e suas pontuações.",
        "!cargop @cargo pontos - Define ou atualiza um cargo para ser atribuído a um usuário quando ele alcançar uma certa quantidade de pontos.",
        "!cargor @cargo - Remove o cargo atribuído a uma quantidade de pontos e não adiciona mais o cargo se não houver nada setado.",
        "!canalp #canal - Define o canal onde o bot enviará notificações sobre cargos.",
        "!canalr - Remove o canal de notificação.",
        "!horasp segundos pontos - Configura a quantidade de pontos que um usuário recebe por ficar em uma chamada de voz.",
        "!cmdp - Mostra todos os comandos do bot e como usá-los.",
        "!cfgp - Mostra os canais e cargos configurados."
    ]

    # Criar o embed com título e cor
    embed = discord.Embed(title="Comandos do Bot", color=discord.Color.blue())
    
    # Adicionar cada comando como um campo no embed
    for command in commands_info:
        # Separando o nome do comando e a descrição
        cmd, description = command.split(" - ")
        embed.add_field(name=cmd, value=description, inline=False)
    
    # Enviar o embed
    await ctx.send(embed=embed)


@client.command()
async def canalp(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("Uso correto: `!canalp #canal`")
        return

    data = load_data()
    data["notify_channel"] = channel.id  # Salva o ID do canal
    save_data(data)
    await ctx.send(f'Canal de notificação definido para {channel.mention}.')

async def assign_role(usuario: discord.Member, pontos: int, roles: dict, notify_channel_id: int):
    current_roles = usuario.roles
    role_added = False  # Para rastrear se um novo cargo foi adicionado

    # Verifica e atribui o cargo mais alto com base na pontuação
    for pontos_limite, role_id in sorted(roles.items(), key=lambda x: int(x[0]), reverse=True):
        if pontos >= int(pontos_limite):
            role = usuario.guild.get_role(role_id)
            if role and role not in current_roles:
                # Remove cargos anteriores antes de adicionar o novo
                for inner_pontos_limite, inner_role_id in sorted(roles.items(), key=lambda x: int(x[0])):
                    if int(inner_pontos_limite) < int(pontos_limite):  # Remove cargos abaixo do limite atual
                        inner_role = usuario.guild.get_role(inner_role_id)
                        if inner_role in current_roles:
                            await usuario.remove_roles(inner_role)
                            if notify_channel_id:  # Se o canal estiver definido
                                channel = usuario.guild.get_channel(notify_channel_id)
                                await channel.send(f'{usuario.name} perdeu o cargo {inner_role.name} por ter mais de {pontos_limite} pontos.')

                await usuario.add_roles(role)  # Adiciona o novo cargo
                role_added = True
                if notify_channel_id:  # Se o canal estiver definido
                    channel = usuario.guild.get_channel(notify_channel_id)
                    await channel.send(f'{usuario.name} recebeu o cargo {role.name} por alcançar {pontos} pontos!')
                break  # Sai do loop após adicionar o cargo

    # Se nenhum cargo foi adicionado e a pontuação é menor que o maior limite, remove todos os cargos
    if not role_added:
        for pontos_limite, role_id in sorted(roles.items(), key=lambda x: int(x[0])):
            if pontos < int(pontos_limite):
                role = usuario.guild.get_role(role_id)
                if role in current_roles:
                    await usuario.remove_roles(role)
                    if notify_channel_id:  # Se o canal estiver definido
                        channel = usuario.guild.get_channel(notify_channel_id)
                        await channel.send(f'{usuario.name} perdeu o cargo {role.name} por ter menos de {pontos_limite} pontos.')

client.run(bot_token)
