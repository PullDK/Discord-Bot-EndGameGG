import discord
import json
import asyncio
from datetime import datetime, timedelta
from DataBase.pontos import carregar_dados

class HoraEmCall:
    def __init__(self, client, id_do_servidor, canal_notificacao):
        self.client = client
        self.id_do_servidor = id_do_servidor
        self.canal_notificacao = canal_notificacao
        self.synced = False
        self.dados = carregar_dados()

    async def start_monitoring(self):
        await self.client.wait_until_ready()
        if not self.synced:
            self.synced = True
        print(f"Entramos como {self.client.user}.")
        # Chamar check_call como uma tarefa assíncrona
        self.client.loop.create_task(self.check_call())

    async def check_call(self):
        while True:
            # Carregar dados do arquivo JSON
            self.dados = carregar_dados()
            hora_especifica_str = self.dados["hora_especifica"]
            hora_especifica = datetime.strptime(hora_especifica_str, "%H:%M").time()

            agora = datetime.now().time()
            if agora >= hora_especifica and agora < (datetime.combine(datetime.today(), hora_especifica) + timedelta(minutes=1)).time():
                # Verifica todos os canais de voz no servidor
                for guild in self.client.guilds:
                    for channel in guild.voice_channels:
                        for member in channel.members:
                            await self.adicionar_pontos(member)
            await asyncio.sleep(45)  # Esperar um minuto antes de checar novamente

    async def adicionar_pontos(self, membro):
        user_id = str(membro.id)
        
        # Atualiza o dicionário de pontos
        if user_id in self.dados['pontos']:
            self.dados['pontos'][user_id] += 5  # Adiciona 5 pontos
        else:
            self.dados['pontos'][user_id] = 5  # Se não existir, inicia com 5 pontos

        await self.enviar_notificacao(membro)

        # Salvar os dados atualizados no JSON
        self.salvar_dados()

    async def enviar_notificacao(self, membro):
        canal_id = self.canal_notificacao.get(str(self.id_do_servidor))
        if canal_id:
            canal = self.client.get_channel(canal_id)
            if canal:
                embed = discord.Embed(
                    title="Notificação de Pontos Adicionados",
                    color=discord.Color.green()
                )
                embed.add_field(name="Pontos:", value="+5", inline=False)
                embed.add_field(name="Usuário:", value=membro.mention, inline=False)
                embed.add_field(name="Motivo:", value="Ficou em call até o horário especificado.", inline=False)
                embed.add_field(name="Quem adicionou os pontos:", value="Sistema", inline=False)
                await canal.send(embed=embed)
            else:
                print(f"Erro: Canal com ID {canal_id} não encontrado.")
        else:
            print(f"Nenhum canal de notificação configurado para o servidor {self.id_do_servidor}.")

    def salvar_dados(self):
        # Função para salvar os dados no arquivo JSON
        with open("dados.json", "w") as f:
            json.dump(self.dados, f, indent=4)

    async def stop_monitoring(self):
        self.monitorando = False
