from socket import *
import threading
from datetime import datetime

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen()
print('Servidor pronto na porta', serverPort)

clientes = {}
trava = threading.Lock()
arquivo_log = open('chat.log', 'a', encoding='utf-8', buffering=1)

def hora():
    return datetime.now().strftime('%H:%M:%S')

def enviar_para_um(sock, texto):
    with trava:
        try:
            sock.sendall((texto + '\n').encode())
        except OSError:
            pass

def enviar_para_todos(texto, excluir=None):
    linha = '[' + hora() + '] ' + texto
    with trava:
        arquivo_log.write(datetime.now().strftime('%Y-%m-%d ') + linha + '\n')
        for nome, sock in list(clientes.items()):
            if nome != excluir:
                try:
                    sock.sendall((linha + '\n').encode())
                except OSError:
                    pass

def atender_cliente(sock, addr):
    sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
    arquivo = sock.makefile('r', encoding='utf-8')
    nome = arquivo.readline().strip()

    with trava:
        if nome == '' or ' ' in nome or nome in clientes:
            aceito = False
        else:
            clientes[nome] = sock
            aceito = True

    if not aceito:
        sock.sendall('ERRO: apelido vazio, com espaco ou ja em uso\n'.encode())
        sock.close()
        return

    sock.sendall('OK\n'.encode())
    print(nome, 'entrou', addr)
    enviar_para_todos('*** ' + nome + ' entrou no chat ***', excluir=nome)

    try:
        for linha in arquivo:
            texto = linha.strip()
            if texto == '':
                continue
            if texto == '/sair':
                break
            elif texto == '/lista':
                with trava:
                    online = ', '.join(clientes)
                enviar_para_um(sock, 'Online: ' + online)
            elif texto == '/ping':
                enviar_para_um(sock, 'PONG')
            else:
                enviar_para_todos(nome + ': ' + texto, excluir=nome)
    except OSError:
        pass

    with trava:
        del clientes[nome]
    print(nome, 'saiu')
    enviar_para_todos('*** ' + nome + ' saiu do chat ***')
    sock.close()

while True:
    connectionSocket, addr = serverSocket.accept()
    threading.Thread(target=atender_cliente, args=(connectionSocket, addr), daemon=True).start()
