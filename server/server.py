import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, send_from_directory

sio = socketio.Server()
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
	if path == '':
		path = 'index.html'
	return send_from_directory('../web/', path)

@sio.on('join')
def join(sid, name):
	raise NotImplementedError

if __name__ == '__main__':
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
