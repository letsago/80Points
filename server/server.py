import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template

sio = socketio.Server()
app = Flask(__name__)

@sio.on('join')
def join(sid, name):
	raise NotImplementedError

if __name__ == '__main__':
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
