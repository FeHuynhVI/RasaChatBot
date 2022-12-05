from flask import Flask, url_for, render_template, request
from flask_socketio import SocketIO, send, emit, Namespace, ConnectionRefusedError, join_room, leave_room

app = Flask(__name__, template_folder='build', static_folder='build')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=True, engineio_logger=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return 'login'


@app.route('/user/<username>')
def profile(username):
    return f'{username}\'s profile'


with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message, namespace='/chat')


@socketio.on('json')
def handle_json(json):
    send(json, json=True, namespace='/chat')


@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', ('foo', 'bar', json), broadcast=True, namespace='/chat')


@socketio.on_error()  # Handles the default namespace
def error_handler(e):
    pass


@socketio.on_error('/chat')  # handles the '/chat' namespace
def error_handler_chat(e):
    pass


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print(request.event["message"])  # "my error event"
    print(request.event["args"])  # (data,)


@socketio.on('connect')
def test_connect(auth):
    # if not self.authenticate(request.args):
    #     raise ConnectionRefusedError('unauthorized!')
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)


class MyCustomNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_my_event(self, data):
        emit('my_response', data)


if __name__ == '__main__':
    socketio.run(app)