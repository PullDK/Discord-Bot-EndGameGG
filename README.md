# Discord Points Bot

Este bot para Discord foi desenvolvido para gerenciar pontos de usuários com base no tempo que passam em chamadas de voz, além de permitir a adição e remoção manual de pontos, atribuição de cargos e notificações de mudanças.

## Requisitos

- Python 3.8 ou superior
- Bibliotecas:
  - `discord.py` (v2.0 ou superior)
  - `json` (incluso no Python)
  - `os` (incluso no Python)

### Instalação

1. Clone o repositório ou baixe o arquivo do bot.
2. Instale a biblioteca `discord.py` usando o pip:

   ```bash
   pip install -U discord.py
   ```

3. Crie um arquivo chamado `apikey.py` no mesmo diretório que o bot e adicione sua chave de bot:

   ```python
   bot_token = "SUA_CHAVE_DO_BOT_AQUI"
   ```

## Estrutura do Código

O código do bot é dividido em várias partes principais:

### 1. Configuração e Inicialização

```python
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
```
- **Intents**: Permitem ao bot receber eventos específicos, como atualizações de estado de voz e mensagens.
- **Prefixo de comando**: O bot responderá a comandos que começam com `!`.

### 2. Manipulação de Dados

O bot usa um arquivo JSON (`data.json`) para armazenar dados de pontos, cargos e canais de notificação dos usuários.

#### Funções de Carregamento e Salvamento de Dados
```python
def load_data():
    if not os.path.exists(data_file):
        return {}  # Retorna um dicionário vazio para novos servidores
    with open(data_file, "r") as file:
        return json.load(file)

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)
```

### 3. Gerenciamento de Pontos em Chamadas de Voz

O bot rastreia quanto tempo os usuários passam em chamadas de voz e recompensa com pontos.

#### Eventos
```python
@client.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)
    # Adiciona pontos quando o usuário entra na chamada
    if after.channel is not None:
        if user_id not in user_voice_times:
            user_voice_times[user_id] = time.time()
    # Atualiza pontos quando o usuário sai da chamada
    else:
        if user_id in user_voice_times:
            duration = time.time() - user_voice_times[user_id]
            await update_points(member, duration)
            del user_voice_times[user_id]
```
- O evento `on_voice_state_update` é acionado quando um membro entra ou sai de um canal de voz.

### 4. Comandos do Bot

Os comandos que os usuários podem usar incluem:

- `!addp @usuario pontos`: Adiciona pontos a um usuário.
- `!remp @usuario pontos`: Remove pontos de um usuário.
- `!allp`: Mostra todos os usuários e suas pontuações.
- `!cargop @cargo pontos`: Define ou atualiza um cargo para ser atribuído a um usuário ao alcançar uma certa quantidade de pontos.
- `!cmdp`: Mostra todos os comandos do bot e como usá-los.

### 5. Atribuição de Cargos

Os cargos são atribuídos com base nos pontos acumulados pelos usuários. O bot remove cargos se a pontuação do usuário cair abaixo do limite para o cargo.

#### Função de Atribuição de Cargo
```python
async def assign_role(usuario: discord.Member, pontos: int, roles: dict, notify_channel_id: int):
    # Lógica para atribuir ou remover cargos baseado na pontuação
```
- O bot irá adicionar ou remover cargos automaticamente com base nos pontos acumulados pelos usuários.

### 6. Notificações

O bot pode enviar notificações em um canal específico quando um usuário recebe ou perde um cargo.

## Como Usar

1. Inicie o bot executando o arquivo Python.
2. Use os comandos listados para gerenciar os pontos e cargos dos usuários.

## Contribuições

Sinta-se à vontade para contribuir com melhorias ou correções. 

## Licença

Este projeto é de código aberto e pode ser usado sob os termos da licença MIT.
