from website import create_app
from flask import request

app, socket = create_app()

@socket.on('message')
def handle_message_event(msg):
    print('[LOG] received msg from {} : {}'.format(request.remote_addr, str(msg)))

if __name__ == '__main__':
    socket.run(app, host="0.0.0.0", debug=True)