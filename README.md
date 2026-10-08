# Chat TCP em Python

Chat feito com sockets TCP, com um servidor e vários clientes. Cada mensagem enviada por um cliente é repassada para todos os outros. O projeto nasceu de um exercício de Redes de Computadores (seção 2.7.2 do livro Redes de Computadores e a Internet) e depois foi melhorado para estudar como a rede se comporta.

## O que o chat faz

- Aceita vários clientes ao mesmo tempo (uma thread por cliente).
- Avisa todo mundo quando alguém entra ou sai.
- Não permite dois usuários com o mesmo apelido.
- Comandos: `/lista` (quem está online), `/ping` (tempo de ida e volta até o servidor) e `/sair`.
- Coloca a hora em cada mensagem e guarda tudo em `chat.log`.
- O cliente mostra quanto tempo levou para a conexão TCP ser feita.
- Funciona entre computadores diferentes, não só no localhost.

## Requisitos

Python 3.8 ou mais novo. Não precisa instalar nada, só usa a biblioteca padrão.

## Como usar

Servidor (no Linux use `python3`):

```
python Server.py
```

Cliente, em outro terminal ou em outro computador:

```
python Client.py
```

O cliente pergunta o IP do servidor, a porta (Enter usa a 12000) e o apelido. Para testar no mesmo computador, use `127.0.0.1`. Para testar entre computadores, use o IP de quem está rodando o servidor (`ipconfig` no Windows, `ip -4 addr` no Linux) e libere a porta 12000 no firewall dele, se for preciso.

## Teste de carga

Cria clientes falsos que mandam mensagens e mostra quantas foram entregues e em quanto tempo:

```
python teste_carga.py IP_DO_SERVIDOR 10 200
```

Os números são: quantidade de clientes e mensagens por cliente. Como cada mensagem vai para todos os outros clientes, o trabalho do servidor cresce rápido quando o número de clientes aumenta.

## Arquivos

| Arquivo | Para que serve |
| --- | --- |
| `Server.py` | Servidor do chat |
| `Client.py` | Cliente do chat |
| `teste_carga.py` | Teste de carga com clientes falsos |
| `GUIA.md` | Experimentos para entender e medir a rede (inclui Wireshark) |
| `versao_1/` | Primeira versão, só com o chat básico |

## Limitações

- As mensagens não têm criptografia, quem estiver na rede consegue ler.
- Não existe senha para entrar.
- Uma thread por cliente e uma lista protegida por um único Lock funcionam bem para poucos usuários, mas ficam pesadas com centenas de clientes.
