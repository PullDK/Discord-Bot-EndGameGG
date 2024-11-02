# Discord Bot de Pontos e Regras

## Descrição
Este bot do Discord é projetado para gerenciar um sistema de pontos e regras dentro de um servidor. Os usuários podem ganhar ou perder pontos com base em ações específicas, e o bot atribui cargos automaticamente com base na quantidade de pontos que um usuário possui.

## Estrutura do Projeto

A estrutura básica do projeto é a seguinte:
```
/comandos
    ├── Adicionar_Pontos.py
    ├── Cargos.py
    ├── Comandos.py
    ├── Editar_regras.py
    ├── Pontos.py
    ├── Regras.py
    └── Remover_Pontos.py
/db
    └── pontos.py
/config
    └── config_cargos.py
dados.json
Main.py
```

## Funcionalidades do Bot

### Comandos

#### 1. Adicionar Pontos (`/adicionar_pontos`)
- **Descrição:** Adiciona uma quantidade específica de pontos a um usuário mencionado.
- **Uso:** `/adicionar_pontos @usuário 10`
- **Funcionamento:**
    - Carrega os dados do arquivo JSON.
    - Verifica se o usuário mencionado já tem pontos registrados. Se sim, adiciona a quantidade especificada; caso contrário, inicializa os pontos desse usuário.
    - Salva as alterações no arquivo JSON.
    - Chama a função `atribuir_cargo` para atualizar o cargo do usuário com base em sua nova quantidade de pontos.

#### 2. Remover Pontos (`/remover_pontos`)
- **Descrição:** Remove uma quantidade específica de pontos de um usuário mencionado.
- **Uso:** `/remover_pontos @usuário 5`
- **Funcionamento:**
    - Carrega os dados do arquivo JSON.
    - Verifica se o usuário tem pontos registrados e subtrai a quantidade especificada, garantindo que o total não fique negativo.
    - Salva os dados atualizados.
    - Chama a função `atribuir_cargo` para garantir que o cargo do usuário seja atualizado de acordo com os pontos restantes.

#### 3. Visualizar Pontos (`/pontos`)
- **Descrição:** Mostra todos os usuários e seus pontos, juntamente com seus respectivos cargos.
- **Uso:** `/pontos`
- **Funcionamento:**
    - Carrega os dados do arquivo JSON.
    - Cria uma embed com uma lista de usuários, seus pontos e os cargos que possuem.
    - Se não houver usuários registrados, informa que nenhum usuário foi encontrado.

#### 4. Configurar Cargos (`/cargos`)
- **Descrição:** Adiciona ou remove cargos com base na quantidade de pontos.
- **Uso:**
    - Para adicionar: `/cargos @cargo 10 20`
    - Para remover: `/cargos @cargo`
- **Funcionamento:**
    - Carrega os dados do arquivo JSON.
    - Se nenhum valor de ponto mínimo ou máximo for fornecido, remove o cargo do JSON.
    - Se valores forem fornecidos, adiciona ou atualiza o cargo no JSON com os limites especificados.
  
#### 5. Gerenciar Regras (`/regras`)
- **Descrição:** Adiciona, lista ou remove regras para ganhar ou perder pontos.
- **Uso:**
    - Para listar regras: `/regras`
    - Para adicionar: `/regras adicionar ganhar 10 "elogiar amigo"`
    - Para remover: `/regras retirar ganhar 1`
- **Funcionamento:**
    - Carrega os dados do arquivo JSON.
    - Se a ação for `adicionar`, verifica se todos os parâmetros necessários estão presentes, cria uma nova regra com um ID único e salva os dados.
    - Se a ação for `id`, lista todas as regras com seus IDs.
    - Se a ação for `retirar`, remove a regra correspondente com base no tipo e ID.

#### 6. Comandos (`/comandos`)
- **Descrição:** Mostra todos os comandos disponíveis e exemplos de uso.
- **Uso:** `/comandos`
- **Funcionamento:**
    - Cria uma embed que lista todos os comandos disponíveis e seus exemplos de uso.

### Funções

#### 1. `carregar_dados()`
- **Descrição:** Carrega dados do arquivo `dados.json`.
- **Funcionamento:**
    - Verifica se o arquivo existe.
    - Se existir, tenta carregar os dados. Se falhar, retorna um dicionário padrão.
    - Se não existir, retorna um dicionário padrão.

#### 2. `salvar_dados(dados)`
- **Descrição:** Salva os dados no arquivo `dados.json`.
- **Funcionamento:**
    - Escreve os dados passados no arquivo JSON com formatação indentada.

#### 3. `atribuir_cargo(usuario)`
- **Descrição:** Atribui ou remove cargos de um usuário com base em seus pontos.
- **Funcionamento:**
    - Obtém os pontos do usuário.
    - Remove cargos que o usuário não atende mais.
    - Atribui o cargo correto com base na quantidade de pontos do usuário.

## Estrutura de Dados

O arquivo `dados.json` possui a seguinte estrutura:

```json
{
    "pontos": {
        "user_id": 100
    },
    "cargos": {
        "cargo_id": {
            "min": 0,
            "max": 100
        }
    },
    "regras": {
        "ganhar": {
            "1": {
                "pontos": 10,
                "descricao": "elogiar amigo"
            }
        },
        "perder": {
            "1": {
                "pontos": -10,
                "descricao": "sair da call"
            }
        }
    }
}
```

- **pontos:** Dicionário onde as chaves são IDs de usuários e os valores são a quantidade de pontos.
- **cargos:** Dicionário onde as chaves são IDs de cargos e os valores são limites de pontos (mínimo e máximo).
- **regras:** Dicionário que contém regras para ganhar ou perder pontos, organizadas por tipo.

## Requisitos
- Python 3.8 ou superior
- Biblioteca `discord.py`

## Instalação

1. Clone este repositório.
2. Instale as dependências necessárias:
   ```bash
   pip install discord.py
   ```
3. Configure seu bot no [Discord Developer Portal](https://discord.com/developers/applications).
4. Substitua as credenciais do bot no seu código conforme necessário.

## Uso

1. Execute seu bot:
   ```bash
   python seu_bot.py
   ```
2. Adicione o bot ao seu servidor e comece a interagir com os comandos disponíveis.

## Contribuição
Sinta-se à vontade para contribuir para este projeto. Faça um fork do repositório, faça suas alterações e envie um pull request.

## Licença
Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para obter mais informações.
