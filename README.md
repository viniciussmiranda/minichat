# Mini-Chat TCP

Sistema de chat multiusuário em Python utilizando sockets TCP.

## Requisitos

- Python 3.7 ou superior
- Biblioteca `socket` (nativa do Python)
- Biblioteca `threading` (nativa do Python)

## Como Executar

### 1. Iniciando o Servidor

O servidor deve ser iniciado primeiro em um PC/terminal.

#### Servidor Local (mesmo computador):
```bash
python server.py
```

#### Servidor em Rede (para aceitar conexões de outros PCs):
```bash
python server.py --host 0.0.0.0 --port 5000
```

**IMPORTANTE:** Use `0.0.0.0` no servidor para aceitar conexões externas!

### 2. Descobrindo o IP do Servidor

Para conectar clientes de outros PCs, você precisa do IP do servidor:

**Windows:**
```bash
ipconfig
```

**Linux/Mac:**
```bash
ip addr
# ou
ifconfig
```

Procure pelo endereço IPv4 na interface de rede ativa (ex: `10.1.13.43`, `192.168.1.100`).

### 3. Conectando Clientes

#### Cliente no mesmo PC do servidor:
```bash
python client.py
```

#### Cliente em outro PC (mesma rede):
```bash
python client.py --host IP_DO_SERVIDOR --port 5000
```

**Exemplo:**
```bash
python client.py --host 10.1.13.43 --port 5000
```

### 4. Registrando seu Nickname

Ao conectar, o cliente solicitará um nickname:

```
Escolha seu NICK: seu_nome_aqui
```

Digite um nick válido (3-20 caracteres, apenas letras, números, `_` ou `-`) e pressione ENTER.

## Comandos Disponíveis

Após conectar e registrar seu nick, você pode usar os seguintes comandos:

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `MSG <texto>` | Envia mensagem para todos (broadcast) | `MSG Olá a todos!` |
| `MSG @nick <texto>` | Envia mensagem direta (DM) | `MSG @maria Como vai?` |
| `WHO` | Lista usuários conectados | `WHO` |
| `QUIT` | Desconecta do chat | `QUIT` |
| `HELP` | Mostra ajuda de comandos | `HELP` |
| `CLEAR` | Limpa a tela | `CLEAR` |

## Exemplo de Uso Completo

### Cenário: 3 pessoas em uma rede local

**PC 1 (Servidor) - IP: 10.1.13.43**
```bash
$ python server.py --host 0.0.0.0 --port 5000
[server] listening on 0.0.0.0:5000
```

**PC 2 (Cliente 1)**
```bash
$ python client.py --host 10.1.13.43 --port 5000
Escolha seu NICK: maria
Bem-vindo(a), maria!

> MSG Olá pessoal!
FROM maria [all]: Olá pessoal!
```

**PC 3 (Cliente 2)**
```bash
$ python client.py --host 10.1.13.43 --port 5000
Escolha seu NICK: joao
Bem-vindo(a), joao!

SYSTEM: User joao joined
FROM maria [all]: Olá pessoal!

> MSG @maria Oi Maria!
TO @maria [dm]: Oi Maria!
```

**PC 4 (Cliente 3)**
```bash
$ python client.py --host 10.1.13.43 --port 5000
Escolha seu NICK: pedro
Bem-vindo(a), pedro!

> WHO
USERS joao, maria, pedro
```

## Testando em Diferentes Cenários

### Mesmo PC (Localhost)
Para testar com múltiplos clientes no mesmo computador:

```bash
# Terminal 1 (Servidor)
python server.py

# Terminal 2 (Cliente 1)
python client.py

# Terminal 3 (Cliente 2)
python client.py

# Terminal 4 (Cliente 3)
python client.py
```

Todos conectarão automaticamente em `127.0.0.1:5000`.

### Rede Local (LAN)
PCs conectados ao mesmo roteador/WiFi:

1. Servidor usa `--host 0.0.0.0`
2. Clientes usam o IP local do servidor (ex: `192.168.1.100`, `10.1.13.43`)

### Internet (Avançado)
Para conectar pela internet, considere:
- **Ngrok**: https://ngrok.com (cria túnel TCP)
- **Port Forwarding**: Requer configuração no roteador
- **VPN**: LogMeIn Hamachi, Radmin VPN

## Resolução de Problemas

### Erro: "Conexão recusada"
- Verifique se o servidor está rodando
- Confirme se está usando o IP correto
- Use `--host 0.0.0.0` no servidor para conexões em rede

### Erro: "Nick já em uso"
- Escolha outro nickname
- Certifique-se de que não há outro cliente com o mesmo nick conectado

### Não consigo digitar o nick
- Clique na janela do terminal para focar
- Aguarde a mensagem de boas-vindas aparecer
- Digite o nick e pressione ENTER

### Firewall bloqueando conexões (Windows)
```bash
netsh advfirewall firewall add rule name="Python Chat" dir=in action=allow program="C:\Python\python.exe" enable=yes
```

Ou desative temporariamente o firewall para testes.

## Estrutura do Projeto

```
minichat/
│
├── server.py           # Servidor TCP
├── client.py           # Cliente TCP
├── PROTOCOL.md         # Documentação do protocolo
├── README.md           # Este arquivo
│
└── tests/
    └── test_protocol.py    # Testes automatizados
```

## Casos de Teste

Execute os testes automatizados com:

```bash
pytest tests/test_protocol.py -v
```

## Autores

- André Luís Gomes da Silva Filho
- Artur Francisco Damascena
- João Vitor Ferreira da Silva
- João Vitor Nascimento Paraizo
- José Heitor Felix Guiamarães
- Vinicius da Silva Miranda

## Licença

Este projeto foi desenvolvido como trabalho acadêmico.
