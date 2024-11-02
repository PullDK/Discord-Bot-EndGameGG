
# EndGameGG

EndGameGG é um bot para Discord desenvolvido em Python, focado em gerenciar pontos, cargos e regras em um servidor. Ele utiliza uma base de dados MySQL para armazenar informações de pontos dos usuários, regras de ganho e perda de pontos, e cargos associados a intervalos de pontos. Esse bot facilita a gamificação dentro do servidor Discord, onde os membros podem acumular ou perder pontos com base em ações específicas.

## Instalação e Configuração

### Pré-requisitos
- **Python 3.8+**
- **Bibliotecas Python:** `mysql-connector-python`, `discord.py`
- **Servidor MySQL** para armazenar dados de pontos, regras e cargos

### Passos de Instalação

1. Clone o repositório do bot:
   ```bash
   git clone <URL do repositório>
   ```
2. Instale as dependências:
   ```bash
   pip install mysql-connector-python discord.py
   ```
3. Configure a conexão ao banco de dados MySQL no código. Atualize as credenciais em `db/MySql.py` com seu `host`, `user`, `password`, e `database`.

4. Inicie o bot executando:
   ```bash
   python main.py
   ```

### Configuração do Banco de Dados
Certifique-se de que o banco de dados MySQL contém as tabelas necessárias. O código criará automaticamente as tabelas `pontos`, `regras` e `cargos` se não existirem.

## Estrutura do Projeto

- **main.py**: Arquivo principal que inicia o bot e registra os comandos.
- **commands/**: Diretório com módulos de comandos, incluindo `pontos`, `cargos`, `regras`, etc.
- **db/**: Diretório contendo o módulo `MySql.py` para operações de banco de dados.

## Comandos Principais

### 1. `/pontos`
Exibe os pontos dos usuários e seus respectivos cargos. Permite que os administradores adicionem ou removam pontos dos usuários.

### 2. `/cargos`
Comando para gerenciar cargos com base nos pontos. Administradores podem adicionar ou remover cargos.

### 3. `/regras`
Gerencia as regras para ganho ou perda de pontos:
   - **Adicionar**: Adiciona uma nova regra de ganhar ou perder pontos.
   - **Listar**: Lista todas as regras atuais, organizadas por tipo.
   - **Remover**: Remove uma regra existente.

## Estrutura das Tabelas no Banco de Dados

- **pontos**
   - `user_id`: ID do usuário no Discord (chave primária)
   - `pontos`: Número de pontos do usuário

- **regras**
   - `id`: Identificador único da regra (chave primária)
   - `tipo`: Indica se a regra é para "ganhar" ou "perder" pontos
   - `descricao`: Descrição da regra
   - `pontos`: Quantidade de pontos associados à regra

- **cargos**
   - `cargo_id`: ID do cargo no Discord (chave primária)
   - `min`: Pontuação mínima necessária para o cargo
   - `max`: Pontuação máxima permitida para o cargo

## Funções Principais

- **carregar_pontos(user_id)**: Carrega os pontos de um usuário específico.
- **salvar_pontos(user_id, pontos)**: Salva ou atualiza a pontuação de um usuário.
- **carregar_regras()**: Carrega todas as regras de ganho e perda de pontos.
- **salvar_regras(dados)**: Salva ou atualiza regras de pontuação.
- **carregar_cargos()**: Carrega todos os cargos definidos no banco de dados.
- **carregar_todos_pontos()**: Retorna todos os pontos dos usuários.

## Exemplo de Uso

### Exibindo as Regras
Usuários podem usar o comando `/regras` para ver as regras de ganho e perda de pontos no servidor.

### Adicionando Pontos
Um administrador pode adicionar pontos a um usuário específico com o comando `/pontos adicionar` e remover pontos com `/pontos remover`.

## Contribuição
Para contribuir com o projeto, crie uma nova branch com suas alterações e envie um pull request. Aguarde a aprovação antes da integração.

## Licença
Este projeto é distribuído sob a licença MIT.
