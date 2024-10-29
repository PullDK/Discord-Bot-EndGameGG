
# Bot de Pontuação para Discord

Este é um bot de Discord desenvolvido em Python com a biblioteca `discord.py`. O bot gerencia um sistema de pontos onde os membros do servidor ganham pontos por atividades, podendo obter cargos específicos ao atingir uma pontuação definida. 

## Funcionalidades

- **Sistema de Pontos**: Adiciona e remove pontos dos membros.
- **Atribuição de Cargos**: Automaticamente atribui cargos com base na pontuação dos membros.
- **Canal de Notificação**: Configura um canal para notificações de alteração de cargos.
- **Persistência de Dados**: Armazena dados em `data.json`.

## Configuração Inicial

1. Clone este repositório e instale o `discord.py`:
   ```bash
   pip install discord.py
   ```
2. Crie um arquivo `apikey.py` com o token do bot do Discord:
   ```python
   bot_token = "SEU_TOKEN_AQUI"
   ```
3. Inicie o bot:
   ```bash
   python bot.py
   ```

## Estrutura de Dados

Os dados são armazenados no arquivo `data.json` com a estrutura abaixo:
- `points`: associa usuários com sua pontuação.
- `roles`: define os cargos recebidos ao atingir determinada pontuação.
- `notify_channel`: ID do canal de notificações.

Exemplo de inicialização dos dados para um novo servidor:
```python
def ensure_guild_data(guild_id):
    data = load_data()
    if str(guild_id) not in data:
        data[str(guild_id)] = {"points": {}, "roles": {}, "notify_channel": None}
        save_data(data)
```

## Comandos do Bot

| Comando                    | Descrição                                                                                               |
|----------------------------|---------------------------------------------------------------------------------------------------------|
| `!addp`                    | Abre um menu para selecionar um usuário e adicionar pontos a ele.                                       |
| `!remp`                    | Abre um menu para selecionar um usuário e remover pontos dele.                                         |
| `!allp`                    | Exibe todos os usuários e suas pontuações, organizados por cargo.                                      |
| `!cargop @cargo pontos`    | Define ou atualiza um cargo a ser atribuído ao usuário ao alcançar a pontuação configurada.         |
| `!cargor @cargo`           | Remove a configuração de pontos associada a um cargo específico.                                       |
| `!canalp #canal`           | Define o canal onde o bot enviará notificações sobre mudanças de cargos.                               |
| `!canalr`                  | Remove o canal de notificação atual do servidor.                                                        |
| `!cfgp`                    | Exibe as configurações de cargos e o canal de notificações do servidor.                                |
| `!cmdp`                    | Exibe todos os comandos disponíveis e uma breve descrição de cada um.                                  |

Exemplo de uso de alguns comandos:

- **Adicionando pontos a um usuário**:
   ```python
   @client.command()
   async def addp(ctx):
       view = discord.ui.View()
       select = discord.ui.Select(placeholder="Selecione um usuário...", min_values=1, max_values=1)

       members_to_add = ctx.guild.members[:25]  # Limita a lista aos primeiros 25 membros
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
   ```

- **Definindo cargos com base na pontuação**:
   ```python
   @client.command()
   async def cargop(ctx, cargo: discord.Role = None, pontos: int = None):
       if cargo is None or pontos is None:
           await ctx.send("Uso correto: `!cargop @cargo pontos`")
           return
       data = load_data()
       guild_id = str(ctx.guild.id)
       if guild_id not in data:
           data[guild_id] = {"points": {}, "roles": {}, "notify_channel": None}

       data[guild_id]["roles"][str(pontos)] = cargo.id
       save_data(data)
       await ctx.send(f'O cargo {cargo.name} foi atribuído a {pontos} pontos para este servidor.')
   ```

## Funções Internas

O bot utiliza funções internas para gerenciar dados e atribuição de cargos.

- **Gerenciamento de Pontos e Cargos**:  
   ```python
   async def add_points(member, points):
       data = load_data()
       user_id = str(member.id)
       if user_id not in data["points"]:
           data["points"][user_id] = 20

       data["points"][user_id] += points
       await assign_role(member, data["points"][user_id], data["roles"], data["notify_channel"])
       save_data(data)
   ```

- **Atribuição de Cargos Automática**:
   ```python
   async def assign_role(usuario: discord.Member, pontos: int, roles: dict, notify_channel_id: int):
       current_roles = usuario.roles
       for pontos_limite, role_id in sorted(roles.items(), key=lambda x: int(x[0]), reverse=True):
           if pontos >= int(pontos_limite):
               role = usuario.guild.get_role(role_id)
               if role and role not in current_roles:
                   await usuario.add_roles(role)
                   if notify_channel_id:
                       channel = usuario.guild.get_channel(notify_channel_id)
                       await channel.send(f'{usuario.name} recebeu o cargo {role.name} por alcançar {pontos} pontos!')
                   break
   ```

Esses trechos destacam algumas das funcionalidades principais e mostram como o bot gerencia pontos e cargos de forma automatizada.

## Exemplo de Uso

1. **Adicionar pontos**: Use `!addp` e selecione o usuário no menu.
2. **Configurar cargo por pontuação**: Use `!cargop @cargo 100` para atribuir o cargo ao atingir 100 pontos.
3. **Visualizar pontuação de todos os membros**: Use `!allp` para exibir a pontuação de todos os usuários.

## Contribuição

Sinta-se à vontade para fazer um fork deste repositório e sugerir melhorias por meio de pull requests. 
