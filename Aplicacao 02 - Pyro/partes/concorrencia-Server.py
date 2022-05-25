# saved as greeting-server.py
import Pyro5.api
import threading
import time

filaRecurso = [[],[]]
listaEnderecos = []

STATUS = ['RELEASED','RELEASED']
timer = [0,0]
usuarioAtual = ['','']

@Pyro5.api.expose
# configura uma instância única do servidor para ser consumida por diversos clientes
@Pyro5.api.behavior(instance_mode="single")
class servidor(object):
    global listaEnderecos
    def requestRecurso(self,recNumber,address):
        print(self)

        exist_count = listaEnderecos.count(address)
        #se já recebeu mensagem, apenas processa o recurso
        if exist_count>0:
            #se o cliente não está na fila do reurso, processa a mensagem, caso contrário, ignora
            if(not filaRecurso[recNumber].count(address) and not usuarioAtual[recNumber]==address):
                processaRecursos(recNumber,address)
        #caso nunca tenha recebido, coloca na lista de endereços, envia a chave, e então processa o recurso
        else:
            cliente = Pyro5.api.Proxy(address)
            cliente.notificacao('chave')
            listaEnderecos.append(address)
            processaRecursos(recNumber,address)

    def freeRecurso(self,recNumber,address):
        global STATUS
        global timer 
        global filaRecurso
        global usuarioAtual
        if STATUS[recNumber] == 'HELD' and usuarioAtual[recNumber] == address:
            STATUS[recNumber] = 'RELEASED'
            timer[recNumber] = 0
            usuarioAtual[recNumber] = ''
            print('Endereço {} liberou o recurso {}'.format(address,(recNumber+1)))
            if(len(filaRecurso[recNumber])):
                address = filaRecurso[recNumber].pop(0)
                processaRecursos(recNumber, address)

        
def processaRecursos(recNumber, address):
    global STATUS
    global timer
    global filaRecurso
    global usuarioAtual
    if STATUS[recNumber] == 'RELEASED':
        STATUS[recNumber] = 'HELD'
        usuarioAtual[recNumber] = address 
        cliente = Pyro5.api.Proxy(address)
        cliente.notificacao(recNumber)
        timer[recNumber] = 30
        print('Endereço {} em posse de recurso {}'.format(address,(recNumber+1)))
    else:
        filaRecurso[recNumber].append(address)

              

def timerWatcher(recNumber):
    global timer
    global STATUS
    global usuarioAtual
    while(1):
        if timer[recNumber] > 0:
            timer[recNumber] -=1
        if timer[recNumber] == 0 and STATUS[recNumber] == 'HELD':
            STATUS[recNumber] = 'RELEASED'
            print('Endereço {} liberou o recurso {}'.format(usuarioAtual[recNumber],(recNumber+1)))
            usuarioAtual[recNumber] = ''
            if(len(filaRecurso[recNumber])):
                address = filaRecurso[recNumber].pop(0)
                processaRecursos(recNumber, address)

        time.sleep(1)


def main():
    daemon = Pyro5.server.Daemon()              # make a Pyro daemon
    ns = Pyro5.api.locate_ns()                  # find the name server
    uri = daemon.register(servidor)             # register the greeting maker as a Pyro object
    ns.register("notificacao.Teste", uri)      # register the object with a name in the name server
    #start timers
    num = 0
    thread = threading.Thread(target=timerWatcher, args=(num,))
    thread.start()
    num = 1
    thread = threading.Thread(target=timerWatcher, args=(num,))
    thread.start()
    print("A aplicação está ativa.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls

if __name__ == "__main__":
    main()