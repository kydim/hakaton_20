from flask import Flask, jsonify
from os import environ

app = Flask(__name__)


@app.route('/test')
def test():
    return jsonify({'test': 'result'})


@app.route('/search_food/<product>')
def search_food(product):
    return jsonify({f'result for {product}': 'food'})


@app.route('/get_state/<chat_id>')
def get(chat_id):
    return jsonify({f'{chat_id}': 'result'})


@app.route('/update_state', methods=['POST'])
def update_state():
    pass


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
