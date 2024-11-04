import discord
import asyncio
import json
import os
from DataBase.pontos import carregar_dados

class VoiceMonitor:
    def __init__(self, client, id_do_servidor):
        self.client = client
        self.id_do_servidor = id_do_servidor
        self.monitorando = True
        self.dados = carregar_dados()
        self.pontos = self.dados["pontos"]
        self.canal_notificacao = self.dados.get("canal_notificacao", {})
        self.tempo_no_canal = {}
        self.membros_em_call = set()

    async def start_monitoring(self):
        while self.monitorando:
            await self.check_voice_channels()
            await asyncio.sleep(5)  # Espera 5 segundos entre verificações

    async def check_voice_channels(self):
        guild = self.client.get_guild(self.id_do_servidor)
        if not guild:
            print(f"Erro: Guild com ID {self.id_do_servidor} não encontrada.")
            return

        membros_atualmente_em_call = set()

        for voice_channel in guild.voice_channels:
            for member in voice_channel.members:
                user_id = str(member.id)
                membros_atualmente_em_call.add(user_id)

                if user_id not in self.membros_em_call:
                    self.membros_em_call.add(user_id)
                    self.tempo_no_canal[user_id] = 0
                    print(f"{member.name} entrou no canal. Tempo inicializado.")

                # Incrementa o tempo em call
                self.tempo_no_canal[user_id] += 5  # Incrementa 5 segundos

                # Verifica se o tempo em call atingiu o limite configurado
                if self.tempo_no_canal[user_id] >= self.obter_tempo_em_call():
                    await self.adicionar_pontos(member)
                    self.tempo_no_canal[user_id] = 0  # Reseta o tempo após adicionar pontos

        # Remove usuários que saíram do canal
        for user_id in list(self.tempo_no_canal.keys()):
            if user_id not in membros_atualmente_em_call:
                del self.tempo_no_canal[user_id]  # Remove o tempo do usuário que saiu
                self.membros_em_call.remove(user_id)  # Remove o usuário do conjunto de membros em call
                print(f"{user_id} saiu do canal. Tempo resetado.")

    async def adicionar_pontos(self, membro):
        user_id = str(membro.id)
        # Atualiza os pontos
        self.pontos[user_id] = self.pontos.get(user_id, 0) + 5
        self.dados["pontos"] = self.pontos  # Atualiza a estrutura de dados com os pontos

        await self.salvar_dados()  # Salva os dados após adicionar pontos
        await self.enviar_mensagem(membro)

    async def salvar_dados(self):
        # Função para salvar os dados de volta no arquivo JSON
        with open("dados.json", "w") as f:
            json.dump(self.dados, f, indent=4)

    async def enviar_mensagem(self, membro):
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
                embed.add_field(name="Motivo:", value=f"Ficou em call por mais de {self.formatar_tempo(self.obter_tempo_em_call())}", inline=False)
                embed.add_field(name="Quem adicionou os pontos:", value="Sistema", inline=False)
                await canal.send(embed=embed)
            else:
                print(f"Erro: Canal com ID {canal_id} não encontrado.")
        else:
            print(f"Nenhum canal de notificação configurado para o servidor {self.id_do_servidor}.")

    def obter_tempo_em_call(self):
        # Carrega os dados atualizados e retorna o tempo em call configurado
        self.dados = carregar_dados()
        return self.dados.get("tempo_em_call", 0)

    def formatar_tempo(self, segundos):
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60
        return f"{horas}h {minutos}m {segundos}s"

    async def stop_monitoring(self):
        self.monitorando = False
