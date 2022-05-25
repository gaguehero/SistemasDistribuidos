import Pyro5.api
import threading
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

recurso = ['RELEASED','RELEASED']
chavePublica = ''
#dicionario dos recursos -> RELEASED = não requisitado, WANTED = requisitado e não atendido, HELD = em uso

@Pyro5.api.expose
@Pyro5.api.callback
class cliente_callback(object):

    def notificacao(self,rec):
        if rec == 0 or rec == 1:
            recurso[rec] = 'HELD'
        else:
            print(rec)
    def loopThread(daemon):
        # thread para ficar escutando chamadas de método do servidor
        daemon.requestLoop()
def main():
    # obtém a referência da aplicação do servidor no serviço de nomes
    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("notificacao.Teste")
    servidor = Pyro5.api.Proxy(uri)
    
    # Inicializa o Pyro daemon e registra o objeto Pyro callback nele.
    daemon = Pyro5.server.Daemon()
    callback = cliente_callback()
    myAdd = daemon.register(callback)
    
    # inicializa a thread para receber notificações do servidor
    thread = threading.Thread(target=cliente_callback.loopThread, args=(daemon, ))
    thread.daemon = True
    thread.start()

    
    while(1):
        global recurso
        recNum = input("Tabela de Seleção\n Digite 1 para Req Recurso 1\n Digite 2 para Req Recurso 2\n Digite 3 para Lib Recurso 1\n Digite 4 para Lib Recurso 2\n Digite 5 para Status dos Recursos\n")
        if int(recNum) == 1 or int(recNum) == 2:
            recurso[int(recNum)-1]='WANTED'
            servidor.requestRecurso(int(recNum)-1,myAdd)
            print('Recurso requisitado \n\n')
        if int(recNum) == 3 and recurso[int(recNum)-1] == 'HELD':
            servidor.freeRecurso(0,myAdd)
            print('Recurso 1 liberado! \n\n')
        if int(recNum) == 4 and recurso[int(recNum)-1] == 'HELD':
            servidor.freeRecurso(1,myAdd)
            print('Recurso 2 liberado! \n\n')
        if int(recNum) == 5:
            print('O Recurso 1 está: {}\nO Recurso 2 está: {}\n\n'.format(recurso[0],recurso[1]))


if __name__ == "__main__":
    main()