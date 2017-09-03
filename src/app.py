import os

import bcrypt
import configparser
from flask import Flask, request, send_from_directory
from flask import render_template, redirect
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

from notes_api import notes_api
from sql import connect
from tree_api import tree_api
from notes_move_api import notes_move_api

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.secret_key = config['Security']['flaskSecretKey']
app.register_blueprint(tree_api)
app.register_blueprint(notes_api)
app.register_blueprint(notes_move_api)

class User(UserMixin):
    pass

@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

@app.route('/app', methods=['GET'])
@login_required
def show_app():
    return render_template('app.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('login')

user = User()
user.id = config['Login']['username']

port = config['Network']['port']
https = config['Network']['https']
certPath = config['Network']['certPath']
certKeyPath = config['Network']['certKeyPath']

documentPath = config['Document']['documentPath']

connect(documentPath)

hashedPassword = config['Login']['password-hash'].encode('utf-8')

@app.route('/login', methods=['POST'])
def login_post():
    inputPassword = request.form['password'].encode('utf-8')

    if request.form['username'] == user.id and bcrypt.hashpw(inputPassword, hashedPassword) == hashedPassword:
        rememberMe = True if 'remember-me' in request.form else False

        login_user(user, remember=rememberMe)

        return redirect('app')
    else:
        return render_template('login.html', failedAuth=True)

CORS(app)

@app.route('/stat/<path:path>')
def send_stc(path):
    return send_from_directory(os.path.join(os.getcwd(), 'static'), path)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_form'

@login_manager.user_loader
def load_user(user_id):
    if user_id == user.id:
        return user
    else:
        return None

if __name__ == "__main__":
    ssl_context = None

    if https == "true":
        ssl_context = (certPath, certKeyPath)

    app.run(host='0.0.0.0', port=port, ssl_context = ssl_context)