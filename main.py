import discord
from discord.ext import commands
import json
import os

from apikey import *  # Certifique-se de que o arquivo de chave API está configurado corretamente

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
        return {}  # Retorna um dicionário vazio para novos servidores
    with open(data_file, "r") as file:
        return json.load(file)

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

# Função para garantir que os dados de um servidor estejam configurados corretamente
def ensure_guild_data(guild_id):
    data = load_data()
    if str(guild_id) not in data:
        data[str(guild_id)] = {"points": {}, "roles": {}, "notify_channel": None}  # Estrutura padrão para novos servidores
        save_data(data)
        


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

class AddPointsModal(discord.ui.Modal):
    def __init__(self, user: discord.Member):
        super().__init__(title="Adicionar Pontos")
        self.user = user
        self.pontos = discord.ui.TextInput(label="Quantidade de Pontos", required=True)

        self.add_item(self.pontos)

    async def on_submit(self, interaction: discord.Interaction):
        pontos = int(self.pontos.value)

        # Carrega os dados do servidor específico
        data = load_data()
        guild_id = str(interaction.guild.id)
        user_id = str(self.user.id)

        # Se o servidor não tiver dados, inicializa
        if guild_id not in data:
            data[guild_id] = {"points": {}, "roles": {}, "notify_channel": None}

        # Inicializa a pontuação do usuário se não existir
        if user_id not in data[guild_id]["points"]:
            data[guild_id]["points"][user_id] = 20

        # Adiciona os pontos ao usuário
        data[guild_id]["points"][user_id] += pontos

        # Atualiza a função de atribuição de cargos e notificação
        await assign_role(
            self.user,
            data[guild_id]["points"][user_id],
            data[guild_id]["roles"],
            data[guild_id]["notify_channel"]
        )

        # Salva os dados atualizados
        save_data(data)
        await interaction.response.send_message(f'{pontos} pontos foram adicionados a {self.user.name}. Pontuação total: {data[guild_id]["points"][user_id]} pontos.')

@client.command()
async def addp(ctx):
    view = discord.ui.View()

    select = discord.ui.Select(
        placeholder="Selecione um usuário...",
        min_values=1,
        max_values=1,
    )

    # Limita o número de membros a 25
    members_to_add = ctx.guild.members[:25]  # Pega apenas os primeiros 25 membros
    for member in members_to_add:
        select.add_option(label=member.name, value=member.id)

    async def select_callback(interaction: discord.Interaction):
        user = ctx.guild.get_member(int(select.values[0]))
        await ctx.send(f"Você selecionou {user.name}.")
        modal = AddPointsModal(user)
        await interaction.response.send_modal(modal)

    select.callback = select_callback
    view.add_item(select)
    await ctx.send("Por favor, selecione um usuário:", view=view)


class RemovePointsModal(discord.ui.Modal):
    def __init__(self, user: discord.Member):
        super().__init__(title="Remover Pontos")
        self.user = user
        self.pontos = discord.ui.TextInput(label="Quantidade de Pontos", required=True)

        self.add_item(self.pontos)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            pontos = int(self.pontos.value)
        except ValueError:
            await interaction.response.send_message("Por favor, insira um número válido de pontos.", ephemeral=True)
            return

        # Carrega os dados específicos do servidor
        data = load_data()
        guild_id = str(interaction.guild.id)
        user_id = str(self.user.id)

        # Verifica se o servidor possui dados e se o usuário existe nos dados
        if guild_id not in data or user_id not in data[guild_id]["points"]:
            await interaction.response.send_message(f'O usuário {self.user.name} não possui pontos registrados neste servidor.', ephemeral=True)
            return

        # Remove os pontos do usuário
        if data[guild_id]["points"][user_id] < pontos:
            await interaction.response.send_message(f'O usuário {self.user.name} não possui pontos suficientes para remover {pontos} pontos.', ephemeral=True)
            return
        
        data[guild_id]["points"][user_id] -= pontos

        # Garante que a pontuação não seja negativa
        if data[guild_id]["points"][user_id] < 0:
            data[guild_id]["points"][user_id] = 0

        # Atualiza o arquivo de dados
        save_data(data)

        # Atualiza os cargos do usuário com a nova pontuação
        await assign_role(
            self.user,
            data[guild_id]["points"][user_id],
            data[guild_id]["roles"],
            data[guild_id]["notify_channel"]
        )

        await interaction.response.send_message(f'{pontos} pontos foram removidos de {self.user.name}. Pontuação atual: {data[guild_id]["points"][user_id]} pontos.')

@client.command()
async def remp(ctx):
    view = discord.ui.View()

    select = discord.ui.Select(
        placeholder="Selecione um usuário...",
        min_values=1,
        max_values=1,
    )

    # Limita o número de membros a 25
    members_to_add = ctx.guild.members[:25]  # Pega apenas os primeiros 25 membros
    for member in members_to_add:
        select.add_option(label=member.name, value=member.id)

    async def select_callback(interaction: discord.Interaction):
        user = ctx.guild.get_member(int(select.values[0]))
        await ctx.send(f"Você selecionou {user.name}.")
        modal = RemovePointsModal(user)
        await interaction.response.send_modal(modal)

    select.callback = select_callback
    view.add_item(select)
    await ctx.send("Por favor, selecione um usuário:", view=view)


@client.command()
async def allp(ctx):
    # Carrega os dados específicos do servidor
    data = load_data()
    guild_id = str(ctx.guild.id)

    # Verifica se o servidor possui dados de pontuação
    if guild_id not in data or not data[guild_id]["points"]:
        await ctx.send("Nenhum usuário registrado neste servidor.")
        return

    # Dicionário para armazenar o cargo mais alto de cada usuário
    cargos = {}

    # Itera sobre cada usuário e identifica o cargo mais alto com base na pontuação
    for user_id, pontos in data[guild_id]["points"].items():
        for pontos_min, role_id in sorted(data[guild_id]["roles"].items(), key=lambda x: int(x[0]), reverse=True):
            if pontos >= int(pontos_min):
                # Atribui o cargo se for o maior que o usuário pode obter
                if user_id not in cargos or int(pontos_min) > cargos[user_id][0]:
                    cargos[user_id] = (int(pontos_min), role_id)
                break  # Para ao encontrar o primeiro cargo que atende aos pontos

    # Agrupa usuários por seus cargos
    usuarios_por_cargo = {}
    for user_id, (pontos_min, role_id) in cargos.items():
        if role_id not in usuarios_por_cargo:
            usuarios_por_cargo[role_id] = []
        usuarios_por_cargo[role_id].append(user_id)

    # Cria o embed
    embed = discord.Embed(
        title="Pontuação dos Usuários",
        color=discord.Color.green()
    )

    # Adiciona campos ao embed para cada cargo
    for pontos_min, role_id in sorted(data[guild_id]["roles"].items(), key=lambda x: int(x[0]), reverse=True):
        if role_id in usuarios_por_cargo:
            role = ctx.guild.get_role(int(role_id))
            if role:
                role_name = role.name
                usuarios_info = "\n".join([f"<@{user_id}>: {data[guild_id]['points'][user_id]} pontos" for user_id in usuarios_por_cargo[role_id]])
                embed.add_field(name=role_name, value=usuarios_info, inline=False)

    # Caso não haja cargos configurados
    if not usuarios_por_cargo:
        embed.description = "Nenhum cargo configurado com usuários."

    await ctx.send(embed=embed)


@client.command()
async def cargop(ctx, cargo: discord.Role = None, pontos: int = None):
    if cargo is None or pontos is None:
        await ctx.send("Uso correto: `!cargop @cargo pontos`")
        return

    # Carrega os dados específicos do servidor
    data = load_data()
    guild_id = str(ctx.guild.id)

    # Inicializa os dados do servidor se ainda não existirem
    if guild_id not in data:
        data[guild_id] = {"points": {}, "roles": {}, "notify_channel": None}

    # Remove cargos existentes com a mesma pontuação, se for necessário
    for pontos_limite in list(data[guild_id]["roles"].keys()):
        if pontos_limite != str(pontos):  # Não remove se a pontuação for a mesma
            if data[guild_id]["roles"][pontos_limite] == cargo.id:
                del data[guild_id]["roles"][pontos_limite]
                break

    # Adiciona ou atualiza a configuração de cargo e pontos
    data[guild_id]["roles"][str(pontos)] = cargo.id
    save_data(data)
    
    await ctx.send(f'O cargo {cargo.name} foi atribuído a {pontos} pontos para este servidor.')


@client.command()
async def cfgp(ctx):
    # Carrega os dados específicos do servidor
    data = load_data()
    guild_id = str(ctx.guild.id)

    # Verifica se o servidor possui dados
    if guild_id not in data:
        await ctx.send("Nenhuma configuração encontrada para este servidor.")
        return

    # Obtém os cargos configurados para o servidor atual
    roles_info = "\n".join(
        [f"{pontos} pontos: <@&{role_id}>" for pontos, role_id in data[guild_id]["roles"].items()]
    ) or "Nenhum cargo configurado."

    # Obtém o canal de notificação configurado para o servidor atual
    notify_channel_info = f"<#{data[guild_id]['notify_channel']}>" if data[guild_id]["notify_channel"] else "Nenhum canal configurado."

    # Cria o embed com as configurações
    embed = discord.Embed(
        title="Configurações do Bot",
        color=discord.Color.blue()
    )

    # Adiciona os campos de informações ao embed
    embed.add_field(name="Cargos Configurados", value=roles_info, inline=False)
    embed.add_field(name="Canal de Notificação", value=notify_channel_info, inline=False)

    # Envia o embed como resposta
    await ctx.send(embed=embed)


@client.command()
async def canalr(ctx):
    # Carrega os dados específicos do servidor
    data = load_data()
    guild_id = str(ctx.guild.id)

    # Verifica se o servidor possui dados e configura o canal de notificação para None
    if guild_id in data:
        data[guild_id]["notify_channel"] = None
        save_data(data)
        await ctx.send("O canal de notificação foi removido para este servidor.")
    else:
        await ctx.send("Nenhuma configuração de canal de notificação encontrada para este servidor.")


@client.command()
async def cargor(ctx, cargo: discord.Role = None):
    if cargo is None:
        await ctx.send("Uso correto: `!cargor @cargo`")
        return

    # Carrega os dados específicos do servidor
    data = load_data()
    guild_id = str(ctx.guild.id)
    role_removed = False  # Para verificar se o cargo foi removido

    # Verifica se o servidor possui dados e iterar sobre os cargos configurados
    if guild_id in data and "roles" in data[guild_id]:
        for pontos_limite in list(data[guild_id]["roles"].keys()):
            if data[guild_id]["roles"][pontos_limite] == cargo.id:
                del data[guild_id]["roles"][pontos_limite]  # Remove o cargo
                role_removed = True
                break

    # Salva e envia a resposta com base na remoção
    if role_removed:
        save_data(data)
        await ctx.send(f'O cargo {cargo.name} foi removido com sucesso deste servidor.')
    else:
        await ctx.send(f'O cargo {cargo.name} não estava associado a nenhuma quantidade de pontos neste servidor.')


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

    # Carrega os dados específicos do servidor
    data = load_data()
    guild_id = str(ctx.guild.id)

    # Inicializa os dados do servidor se ainda não existirem
    if guild_id not in data:
        data[guild_id] = {"points": {}, "roles": {}, "notify_channel": None}

    # Define o canal de notificação para o servidor atual
    data[guild_id]["notify_channel"] = channel.id
    save_data(data)
    await ctx.send(f'Canal de notificação definido para {channel.mention} neste servidor.')


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
