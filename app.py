from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'API działa!'

@app.route('/trends')
def get_trends():
    return jsonify({'status': 'ok', 'message': 'Test dziala'})
