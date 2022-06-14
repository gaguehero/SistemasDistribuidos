from ast import arg
from inspect import ArgSpec
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sse import sse
import threading
import time

app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

filaRecurso = [[],[]]
listaEnderecos = []

STATUS = ['RELEASED','RELEASED']
timer = [0,0]
usuarioAtual = ['','']

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/sub', methods=['POST'])
def subscibe():
    if request.method == 'POST':
        id = int(request.args['id'])
        recurso = int(request.args['recurso'])
        print(id, recurso)
        processaRecursos(recurso,id)
        return 'OK', 200

@app.route('/release', methods=['POST'])
def release():
    if request.method == 'POST':
        global STATUS
        global timer 
        global filaRecurso
        global usuarioAtual
        id = int(request.args['id'])
        recurso = int(request.args['recurso'])
        if STATUS[recurso] == 'HELD' and usuarioAtual[recurso] == id:
            STATUS[recurso] = 'RELEASED'
            timer[recurso] = 0
            usuarioAtual[recurso] = ''
            print('Endereço {} liberou o recurso {}'.format(id,(recurso+1)))
            if(len(filaRecurso[recurso])):
                id = filaRecurso[recurso].pop(0)
                processaRecursos(recurso, id)
        return 'Ok',200

def processaRecursos(recurso, id):
    global STATUS
    global timer
    global filaRecurso
    global usuarioAtual
    if STATUS[recurso] == 'RELEASED':
        STATUS[recurso] = 'HELD'
        usuarioAtual[recurso] = id 
        notificar(recurso,id)
        timer[recurso] = 30
        print('Endereço {} em posse de recurso {}'.format(id,(recurso+1)))
    else:
        filaRecurso[recurso].append(id)

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
                with app.app_context():
                    processaRecursos(recNumber, address)

        time.sleep(1)

def notificar(recurso, id):
    canal = "recurso{}".format(id)
    msg = "uso do recurso {} autorizado!".format(recurso)
    print(canal)
    sse.publish({"message": msg, "recurso":recurso},type='autorizacao', channel=canal)

#start timers
num = 0
thread = threading.Thread(target=timerWatcher, args=(num,))
thread.start()

num = 1
thread = threading.Thread(target=timerWatcher, args=(num,))
thread.start()
print("A aplicação está ativa.")


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)