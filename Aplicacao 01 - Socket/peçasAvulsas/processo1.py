import socket
import sys
from _thread import *
import threading
import time
import json
import struct

# listaDeEnderecos = ['6666','12345','7895']
# types of messages = ['OK','WANTED']
# types of status = ['WANTED', 'RELEASED', 'HELD']

STATUS = "RELEASED"
timestampado = ''
minhaPorta = '6666'
listaDeMensagens = []
ackNeeded = 0
print_lock = threading.Lock()

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

#listener multicast
def startMulticaster():
    #inicia multicast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    #reuseaddr permite mais de uma dupla ip-porta utilizando o processo
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    while True:
        mensagem = sock.recv(1024).decode()
        jsonMens = json.loads(mensagem)
        #responde mensagens diferentes
        if jsonMens['address'] != minhaPorta:
            processaMsg(jsonMens)

#função para ouvir outros processos
def startListener():
    s = socket.socket()
    port = minhaPorta
    s.bind(('127.0.0.1',int(port)))
    print("socket binded to %s" %(port))
    s.listen(5)
    print("Socket is listening")
    while True:
        c, addr = s.accept()
        #print('mensagem recebida', addr)
        #c.send('connected'.encode())        
        mensagem = c.recv(1024).decode()
        jsonMens = json.loads(mensagem)
        #responde mensagens diferentes
        if jsonMens['address'] != minhaPorta:
            processaMsg(jsonMens)


#função para enviar mensagens unicast para outros processos
def envioUnicast(mensagem,port):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('127.0.0.1',int(port)))
    soc.send(mensagem.encode())
    soc.close()

#função para enviar mensagens multicast para outros processos
def envioMulticast(mensagem):
    MULTICAST_TTL = 2

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    sock.sendto(mensagem.encode(), (MCAST_GRP, MCAST_PORT))

#função para criar o formato da mensagem
def createMessage(de,para,timestamp, status):
    #cria mensagem
    mensagem = {
                'address':de,
                'timestamp': timestamp, 
                'status':status
               }
    jsonMens = json.dumps(mensagem)
    #envia mensagem
    if para == 'todos':
        envioMulticast(jsonMens)
    else:
        envioUnicast(jsonMens,para)


def processaMsg(msg):
    global ackNeeded
    global listaDeMensagens
    #se é uma mensagem de requisição de recurso
    if msg['status'] == 'WANTED':
        #se o status do processo é de livre OU se o timestampo do pedido for menor
        if STATUS == 'RELEASED' or (STATUS == 'WANTED' and float(msg['timestamp']) < timestampado):
            createMessage(minhaPorta, msg['address'], time.time(),'OK')
        else:
            listaDeMensagens.append(msg)
    #se é uma mensagem de autorização de uso
    if msg['status'] == 'OK':
        ackNeeded -=1



def run():
    global ackNeeded
    global STATUS
    global listaDeMensagens
    global timestampado
    print_lock.acquire()
    t = start_new_thread(startListener, ())
    t = start_new_thread(startMulticaster, ())
    print('status do processo 1 ' + STATUS)
    time.sleep(1)
    while True:
        value = input("Quer REQUISITAR o recurso?\n")
        if value:
            
            STATUS = 'WANTED'
            print('status do processo 1 ' + STATUS)
            ackNeeded = 2
            timestampado = time.time()
            createMessage(minhaPorta,'todos',timestampado, STATUS)
        #espera a altorização do recurso
        while(ackNeeded):
            time.sleep(1)
        STATUS = 'HELD'
        print('status do processo 1 ' + STATUS)
        value = input("Quer LIBERAR o recurso?\n")
        if value:
            STATUS = 'RELEASED'
            print('status do processo 1 ' + STATUS)
            #se existe mensagem na fila, libera
            while(len(listaDeMensagens)):
                aux = listaDeMensagens.pop(0)
                createMessage(minhaPorta,aux['address'],time.time(), 'OK')
        

if __name__== '__main__':
    run()
