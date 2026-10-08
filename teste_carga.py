from socket import *
import threading
import time
import sys

host = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10
M = int(sys.argv[3]) if len(sys.argv) > 3 else 100
porta = int(sys.argv[4]) if len(sys.argv) > 4 else 12000

recebidas = 0
ultima = time.perf_counter()
trava = threading.Lock()
socks = []

def contar(arquivo):
    global recebidas, ultima
    for linha in arquivo:
        if linha.rstrip().endswith(': carga'):
            with trava:
                recebidas += 1
                ultima = time.perf_counter()

for i in range(N):
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
    s.connect((host, porta))
    arq = s.makefile('r', encoding='utf-8')
    s.sendall(('bot%d_%d\n' % (i, int(time.time()) % 10000)).encode())
    if arq.readline().strip() != 'OK':
        sys.exit('servidor recusou um bot')
    threading.Thread(target=contar, args=(arq,), daemon=True).start()
    socks.append(s)
print(N, 'clientes conectados. Enviando', N * M, 'mensagens...')

def enviar(s):
    for _ in range(M):
        s.sendall(b'carga\n')

inicio = time.perf_counter()
ts = [threading.Thread(target=enviar, args=(s,)) for s in socks]
for t in ts: t.start()
for t in ts: t.join()
t_envio = time.perf_counter() - inicio

esperado = N * M * (N - 1)
while time.perf_counter() - ultima > 0 and recebidas < esperado:
    time.sleep(0.2)
    if time.perf_counter() - ultima > 3:
        break
total = ultima - inicio
print('Mensagens enviadas pelos bots:', N * M)
print('Entregues: %d de %d esperadas' % (recebidas, esperado))
print('Tempo ate a ultima entrega: %.2f s (%.0f entregas/s)' % (total, recebidas / total if total > 0 else 0))
for s in socks: s.close()
