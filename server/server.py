import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, send_from_directory

import model

NUM_PLAYERS = 4

class User(object):
	def __init__(self, sid, name):
		self.sid = sid
		self.name = name

class ServerState(object):
	def __init__(self):
		self.users = []
		self.round = None

class TimedActionListener(model.RoundListener):
	def __init__(self):
		self.pending_tick = None

	def timed_action(self, r, delay):
		'''
		Run tick on the round after the given delay.

		If there is already a queued tick, we should cancel that tick and reschedule
		it. This may happen if another action was performed on the Round before the
		timed action.
		'''
		def run_action():
			r.tick()
			self.pending_tick = None
		if self.pending_tick is not None:
			self.pending_tick.cancel()
		self.pending_tick = eventlet.spawn_after(delay, run_action)

class ForwardToUser(model.RoundListener):
	'''
	Forwards updates on the Round to a user via sio messages.
	'''

	def __init__(self, sio, player, sid):
		self.sio = sio
		self.player = player
		self.sid = sid

	def _send_state(self, r):
		view = r.get_state().get_player_view(self.player)
		self.sio.emit('state', view, room=self.sid)

	def card_dealt(self, r, player, card):
		data = {
			'player': player,
		}
		if player == self.player:
			data['card'] = card
		self.sio.emit('card_dealt', data, room=self.sid)
		self._send_state(r)

	def player_declared(self, r, player, cards):
		data = {
			'player': player,
			'cards': cards,
		}
		self.sio.emit('player_declared', data, room=self.sid)
		self._send_state(r)

	def player_given_bottom(self, r, player, cards):
		data = {
			'player': player,
		}
		if player == self.player:
			data['cards'] = cards
		self.sio.emit('player_given_bottom', data, room=self.sid)
		self._send_state(r)

	def player_set_bottom(self, r, player, cards):
		data = {
			'player': player,
		}
		if player == self.player:
			data['cards'] = cards
		self.sio.emit('player_set_bottom', data, room=self.sid)
		self._send_state(r)

	def player_played(self, r, player, cards):
		data = {
			'player': player,
			'cards': cards,
		}
		self.sio.emit('player_played', data, room=self.sid)
		self._send_state(r)

sio = socketio.Server()
app = Flask(__name__)
state = ServerState()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
	if path == '':
		path = 'index.html'
	return send_from_directory('../web/', path)

@sio.on('join')
def join(sid, name):
	if state.round is not None:
		sio.emit('bye', 'The game has already started!')
		return

	state.users.append(User(sid, name))
	user_names = [user.name for user in state.users]
	for user in state.users:
		sio.emit('lobby', user_names, room=user.sid)

	# if we have enough users, we can start the game
	if len(state.users) >= NUM_PLAYERS:
		listeners = [TimedActionListener()]
		for i in xrange(len(state.users)):
			listeners.append(ForwardToUser(sio, i, state.users[i].sid))
		state.round = model.Round(len(state.users), listeners)

if __name__ == '__main__':
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
