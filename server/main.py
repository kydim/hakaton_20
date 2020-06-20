from flask import Flask, jsonify
from os import environ

app = Flask(__name__)

from server.client import Client


mongo_client = Client()


@app.route('/test')
def test():
    return jsonify({'test': 'result'})


@app.route('/search_food/<product>')
def search_food(product):
    return jsonify({f'result for {product}': 'food'})


# @app.route('/update_state', methods=['POST'])
@app.route('/update_state')
def update_state():
    mongo_client.update_state(1, {'chat_id': 1, 'data': 4444})
    return jsonify({'result': 'ok'})


@app.route('/get_state/<chat_id>')
def get_state(chat_id):
    data = mongo_client.get_state(chat_id)
    return jsonify(data)


@app.route('/get_data')
def get_data():
    data = mongo_client.get_data('posts')
    short_data = data[100:]
    return jsonify(short_data)


if __name__ == '__main__':
    try:
        try:
            HOST = environ.get('SERVER_HOST', '0.0.0.0')
        except ValueError:
            HOST = '0.0.0.0'
        try:
            PORT = int(environ.get('SERVER_PORT', '5555'))
        except ValueError:
            PORT = 5555
    except AttributeError:
        HOST = '0.0.0.0'
        PORT = 5555
    app.run(HOST, PORT, debug=True)
