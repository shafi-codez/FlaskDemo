__author__ = 'shafi'

import logging
import json,os
import socket
from json2html import *

from flask import Flask, url_for, request,render_template
from flask import Response
from flask import jsonify
from functools import wraps

app = Flask(__name__)


def check_auth(username, password):
    return username == 'admin' and password == 'password'

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Are you Sure ? if No Click cancel"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

@app.route('/')
def home():
    return "<center><br><b>Welcome to Flask !!!</br></br> This is just Demo 1"


@app.route('/demo1', methods = ['GET'])
def api_hello():
    """Print available functions."""
    data = {
        'hello'  : 'world',
        'number' : 3
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://luisrei.com'

    return resp

@app.route('/demo2')
#@requires_auth
def api_hi():
    """Print with name /name?shafi"""
    if 'name' in request.args:
        return 'Hello ' + request.args['name']
    else:
        return 'Hello John Doe'

@app.route('/demo3')
@requires_auth
def api_authmsg():
    """Print secret message after authentication."""
    return "Exposing top secret spy stuff !!"

@app.route('/demo3-ldap/<name>')
def demo3_extn(name):
    """Print secret message after authentication."""
    return getid(name)

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/demo4', methods = ['GET'])
def demo4():
    """Print available functions."""
    msg = 'This msg is from index.html, but templated!'
    return render_template('index.html', res=msg)

@app.route('/demo5', methods = ['GET'])
def demo5():
    """Print available functions."""
    cmd = 'aws ec2 describe-regions'
    running = os.popen(cmd)
    op = json.load(running)
    return render_template('index.html', res=op)


@app.route('/api/help', methods = ['GET'])
def help():
    """<b>Print available functions as json.<br>"""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

def getid(username):
    cmd =("ldapsearch -x -h <server_host_name> -p 389 -b 'ou=People,o=<company_name>' uid={0} | grep mail | cut -d':' -f 2").format(username)
    emailId = os.popen(cmd).read().replace(' ','')
    print emailId
    if len(emailId) > 0:
        return emailId
    else:
        return None

def gethost():
    return str(socket.gethostbyname(socket.gethostname()))

if __name__ == '__main__':
    file_handler = logging.FileHandler('./app.log')
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.run(debug=True, port=80,host='127.0.0.1')

