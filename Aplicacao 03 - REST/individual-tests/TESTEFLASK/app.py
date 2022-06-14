from ast import arg
from inspect import ArgSpec
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sse import sse

app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

data = list(range(1,300,3))
print (data)

def publishHello(id,rec):
    canal = "recurso{}".format(id)
    msg = "uso do recurso {} autorizado!".format(rec)
    print(canal)
    sse.publish({"message": msg},type='autorizacao', channel=canal)

@app.route('/')
def home_page():
    example_embed='This string is from python'
    return render_template('index.html', embed=example_embed)

@app.route('/test', methods=['GET', 'POST'])
def testfn():
    # GET request
    if request.method == 'GET':
        message = {'greeting':'Hello from Flask!'}
        return jsonify(message)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        id = request.args['id']
        recurso = request.args['recurso']
        print(id, recurso)
        print(recurso)
        publishHello(id,recurso)
        return 'OK', 200

@app.route('/getdata/<index_no>', methods=['GET','POST'])
def data_get(index_no):
    
    if request.method == 'POST': # POST request
        print(request.get_json())  # parse as text
        return 'OK', 200
    
    else: # GET request
        return 't_in = %s ; result: %s ;'%(index_no, data[int(index_no)])

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)