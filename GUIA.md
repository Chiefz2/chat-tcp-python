# Chat TCP - versão 2: guia para entender e medir

## O que tem de novo
- Apelido único: o servidor recusa apelido repetido, vazio ou com espaço.
- `/lista` mostra quem está online. `/ping` mede o tempo de ida e volta até o servidor. `/sair` sai do chat.
- Cada mensagem aparece com a hora, e o servidor guarda tudo no arquivo `chat.log`.
- Funciona entre máquinas: o servidor usa `bind(('', 12000))`, que escuta em todas as placas de rede.
- O cliente mostra quanto tempo levou para a conexão TCP ser criada.
- `teste_carga.py` cria vários clientes falsos para ver quanto o servidor aguenta.

## Como rodar
Servidor: `python Server.py`
Cliente: `python Client.py` (pede IP, porta e apelido; Enter na porta usa a 12000)
Carga: `python teste_carga.py IP_DO_SERVIDOR 10 200` (10 clientes, 200 mensagens cada)

## Protocolo (a "conversa" entre cliente e servidor)
Tudo é texto, uma mensagem por linha (termina em `\n`). O TCP é um fluxo de bytes sem fronteira de mensagem, então o `\n` é o que separa uma mensagem da outra.

1. Cliente conecta e manda o apelido.
2. Servidor responde `OK` ou `ERRO: ...`.
3. Depois disso, qualquer linha comum vira mensagem para todos. Linhas que começam com `/` são comandos.

## Experimentos para entender de verdade

### 1. A apresentação de três vias
Ao conectar, o cliente imprime "Conexão TCP feita em X ms". Esse tempo é mais ou menos uma ida e volta de rede (SYN, SYN-ACK, ACK). Compare em `127.0.0.1` com o servidor de outra máquina. Em localhost fica perto de 0,3 ms; na rede da faculdade deve ser maior.

### 2. Latência: `/ping` do chat contra o `ping` do Windows
Digite `/ping` no chat e rode `ping IP_DO_SERVIDOR` no PowerShell. O `ping` do Windows usa ICMP, direto na camada de rede. O `/ping` do chat passa por TCP, pelo Python e por uma thread do servidor, então tende a dar um valor maior. A diferença mostra o custo da aplicação.

### 3. Teste de carga
Rode `python teste_carga.py IP 10 200` e anote "Entregues" e "entregas/s". Depois mude os números:
- Aumente os clientes (10, 30, 60) com as mensagens fixas.
- Cada mensagem enviada é copiada para os outros N-1 clientes, então o trabalho do servidor cresce com o quadrado do número de clientes. Veja se os seus números mostram isso.
- Repita com o servidor em outra máquina e compare com o localhost.

### 4. Wireshark
Filtro de captura/exibição: `tcp.port == 12000`
- **Na rede entre duas máquinas:** capture na placa Ethernet.
- **No localhost do Windows:** o Wireshark precisa do Npcap com a opção de captura de loopback ("Adapter for loopback traffic capture"). Em computador do laboratório, pode não estar instalado ou não ter permissão.

O que procurar:
- **Conexão:** três pacotes `[SYN]`, `[SYN, ACK]`, `[ACK]`. Compare o tempo entre eles com o "Conexão TCP feita em" do cliente.
- **Cada mensagem:** um pacote `[PSH, ACK]` do cliente para o servidor, e o servidor responde com `[ACK]`. Clique com o botão direito em um deles, **Follow > TCP Stream**, e você vai ler o texto do chat puro. O chat não tem criptografia, qualquer um na rede consegue ler.
- **Broadcast:** quando um cliente manda uma mensagem, o servidor manda um pacote separado para cada outro cliente.
- **Saída:** `/sair` gera `[FIN, ACK]`, e o outro lado responde com `[FIN, ACK]` e `[ACK]`.

## Duas ideias que aparecem no código
- **`TCP_NODELAY`:** por padrão o TCP espera um pouco para juntar dados pequenos em um pacote só (algoritmo de Nagle). Para chat isso atrapalha, então o código desliga esse comportamento.
- **Thread por cliente:** simples de entender, e cada cliente tem sua própria "linha de raciocínio" no servidor. O custo é memória e troca de contexto quando há muitos clientes. A alternativa é um laço só com `select`, que fica esperando vários sockets ao mesmo tempo.

## Limitações conhecidas
- Uma lista de clientes protegida por um único `Lock`: se um cliente lento trava o envio, os outros esperam junto.
- Sem criptografia e sem senha.
- Se o cliente fechar de repente, o servidor só percebe quando a leitura falha.
