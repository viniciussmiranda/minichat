# Protocolo Mini-Chat TCP

## Conexão
- Transporte: TCP
- Codificação: UTF-8
- Delimitador: `\n` (linha)

## Handshake / Registro de NICK
1. Servidor → Cliente: `WELCOME Choose a nickname with: NICK <apelido>`
2. Cliente → Servidor: `NICK <apelido>`
3. Servidor → Cliente:
   - Sucesso: `OK nick <apelido>` e broadcast `SYSTEM: User <apelido> joined` para os demais
   - Erros: `ERR nickname_in_use` | `ERR invalid_nick` | `ERR identify_with_NICK_first`

**Regra de apelido**: 3–20 caracteres; letras, números, `_` e `-`.

## Mensagens
### Broadcast
- Cliente → Servidor: `MSG <texto>`
- Servidor → Todos (inclui eco ao remetente): `FROM <nick> [all]: <texto>`

### Direta (DM)
- Cliente → Servidor: `MSG @destinatario <texto>`
- Servidor → Destinatário: `FROM <nick> [dm]: <texto>`
- Servidor → Remetente: `TO @destinatario [dm]: <texto>`
- Erro: `ERR user_not_found`

## WHO
- Cliente → Servidor: `WHO`
- Servidor → Cliente: `USERS <nick1>, <nick2>, ...`

## QUIT
- Cliente → Servidor: `QUIT`
- Servidor → Cliente: `BYE` e fecha conexão
- Servidor → Todos: `SYSTEM: User <nick> left`

## Mensagens de Sistema e Erro
- Sistema (broadcast): `SYSTEM: User <nick> joined|left`
- Erros gerais: `ERR unknown_command`, `ERR invalid_dm_format`

## Exemplos
```
> NICK ana
OK nick ana
SYSTEM: User ana joined

> MSG Olá a todos!
FROM ana [all]: Olá a todos!

> MSG @joao você pode me ajudar?
TO @joao [dm]: você pode me ajudar?
FROM ana [dm]: você pode me ajudar?   # (recebido no cliente do joao)

> WHO
USERS ana, joao, bia

> QUIT
BYE
```
