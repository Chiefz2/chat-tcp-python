from socket import *
import threading

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen()
print('Servidor pronto na porta', serverPort)

clientes = []
trava = threading.Lock()

def enviar_para_todos(mensagem, quem_enviou=None):
    with trava:
        lista = list(clientes)
    for sock, nome in lista:
        if sock != quem_enviou:
            try:
                sock.send((mensagem + '\n').encode())
            except OSError:
                pass

def atender_cliente(connectionSocket, addr):
    arquivo = connectionSocket.makefile('r', encoding='utf-8')
    nome = arquivo.readline().strip()
    if nome == '':
        connectionSocket.close()
        return

    with trava:
        clientes.append((connectionSocket, nome))
    print(nome, 'entrou', addr)
    enviar_para_todos('*** ' + nome + ' entrou no chat ***', connectionSocket)

    try:
        for linha in arquivo:
            texto = linha.strip()
            if texto != '':
                enviar_para_todos(nome + ': ' + texto, connectionSocket)
    except OSError:
        pass

    with trava:
        clientes.remove((connectionSocket, nome))
    print(nome, 'saiu')
    enviar_para_todos('*** ' + nome + ' saiu do chat ***')
    connectionSocket.close()

while True:
    connectionSocket, addr = serverSocket.accept()
    t = threading.Thread(target=atender_cliente, args=(connectionSocket, addr), daemon=True)
    t.start()
