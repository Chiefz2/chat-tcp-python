from socket import *
import threading
import os

serverName = input('IP do servidor: ')
serverPort = 12000
nome = input('Seu nome: ')

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
clientSocket.send((nome + '\n').encode())
print('Conectado! Digite suas mensagens. Para sair digite: sair')

def receber():
    while True:
        try:
            dados = clientSocket.recv(1024)
        except OSError:
            break
        if not dados:
            break
        print(dados.decode(), end='')
    print('Conexao encerrada.')
    os._exit(0)

threading.Thread(target=receber, daemon=True).start()

while True:
    mensagem = input()
    if mensagem == 'sair':
        break
    clientSocket.send((mensagem + '\n').encode())

clientSocket.close()
