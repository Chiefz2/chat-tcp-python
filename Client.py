from socket import *
import threading
import time
import os

serverName = input('IP do servidor: ')
porta = input('Porta (Enter = 12000): ')
serverPort = int(porta) if porta else 12000
nome = input('Seu apelido: ')

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)

inicio = time.perf_counter()
clientSocket.connect((serverName, serverPort))
print('Conexao TCP feita em %.1f ms' % ((time.perf_counter() - inicio) * 1000))

arquivo = clientSocket.makefile('r', encoding='utf-8')
clientSocket.sendall((nome + '\n').encode())
resposta = arquivo.readline().strip()
if resposta != 'OK':
    print(resposta)
    clientSocket.close()
    raise SystemExit
print('Conectado! Comandos: /lista  /ping  /sair')

t_ping = 0.0

def receber():
    for linha in arquivo:
        if linha.strip() == 'PONG':
            print('Ida e volta ate o servidor: %.1f ms' % ((time.perf_counter() - t_ping) * 1000))
        else:
            print(linha, end='')
    print('Conexao encerrada.')
    os._exit(0)

threading.Thread(target=receber, daemon=True).start()

while True:
    mensagem = input()
    if mensagem == '/ping':
        t_ping = time.perf_counter()
    clientSocket.sendall((mensagem + '\n').encode())
    if mensagem == '/sair':
        break

clientSocket.close()
