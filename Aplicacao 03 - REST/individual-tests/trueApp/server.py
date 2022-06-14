import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

filaRecurso = [[],[]]
listaEnderecos = []

STATUS = ['RELEASED','RELEASED']
timer = [0,0]
usuarioAtual = ['','']

@app.route("/", methods=['GET'])
def get_status():
    return "<h1>{}</h1><h1>{}</h1>".format(STATUS[0],STATUS[1])

@app.route("/subscribe", methods=['POST'])
def requestRecurso():
    print(request.get_json())
    return '',204