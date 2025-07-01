import os, sys
# chèn thư mục libs vào front của sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
SYS_LIBS = os.path.join(ROOT, 'libs')
sys.path.insert(0, SYS_LIBS)
from flask import Flask, jsonify, render_template
from state import state

app = Flask(__name__)

@app.route('/api/status')
def get_status():
    return jsonify(state)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', state=state)