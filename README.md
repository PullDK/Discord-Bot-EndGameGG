# Criando um arquivo README.md para o bot de Discord.

readme_content = """
# Discord Bot

Este é um bot de Discord desenvolvido para gerenciar pontos de usuários em um servidor. Ele permite que os administradores adicionem ou removam pontos dos usuários, além de gerenciar regras de ganhos e perdas de pontos.

## Funcionalidades

- **Adicionar Pontos**: Permite que os administradores adicionem pontos a um usuário mencionado.
- **Remover Pontos**: Permite que os administradores removam pontos de um usuário mencionado.
- **Gerenciar Regras**: Os administradores podem definir e editar regras que concedem ou removem pontos com base em ações dos usuários.
- **Visualizar Pontos**: Os usuários podem verificar seus pontos atuais e os de outros usuários.

## Comandos Disponíveis

- `/adicionar_pontos @usuario quantidade` - Adiciona uma quantidade específica de pontos a um usuário mencionado.
- `/remover_pontos @usuario quantidade` - Remove uma quantidade específica de pontos de um usuário mencionado.
- `/editar_regras tipo id_regra novos_pontos nova_descricao` - Edita uma regra existente de ganhar ou perder pontos.
- `/ver_regras` - Exibe todas as regras atuais de ganho e perda de pontos.

## Estrutura do Projeto

- `main.py`: O arquivo principal onde o bot é inicializado e os comandos são registrados.
- `commands/`: Diretório contendo todos os comandos do bot.
- `db/`: Diretório que contém funções para carregar e salvar dados (pontos e regras).
- `config/`: Diretório para configurações e funções auxiliares, como atribuição de cargos.

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/SeuUsuario/SeuRepositorio.git
   cd SeuRepositorio
