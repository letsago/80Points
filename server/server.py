import argparse
import eventlet
import eventlet.wsgi
from flask import Flask, send_from_directory
import random
import socketio
import uuid

import model
import server_utils

parser = argparse.ArgumentParser()
parser.add_argument('--speed', default=5)
parser.add_argument('--debug', action='store_true')
parser.add_argument('--deck_name')

args = parser.parse_args()

class User(object):
	def __init__(self, sid, name):
		self.sid = sid
		self.name = name
		self.game_player = None
		self.left = False

class GamePlayer(object):
	def __init__(self, user, game, observer=False, idx=None):
		self.user = user
		self.game = game
		self.observer = observer
		self.idx = idx
		self.ready = False
		self.listener = None

STATUS_LOBBY = 'lobby'
STATUS_ROUND = 'round'
STATUS_SCORE = 'score'

class Game(model.RoundListener):
	def __init__(self, sio, id, name, num_players):
		self.sio = sio
		self.id = id
		self.name = name
		self.status = STATUS_LOBBY
		self.players = [None] * num_players
		self.round = None

		# players observing this game, sid->GamePlayer
		self.observers = {}

	# Return index of an empty slot, or None if no such slot.
	def _find_empty_slot(self):
		for i in range(len(self.players)):
			if self.players[i] is None:
				return i
		return None

	def _send_lobby(self, player):
		self.sio.emit('lobby', self.lobby_dict(player.idx), room=player.user.sid)

	def _broadcast_lobby(self):
		for player in self.players + self.observers.values():
			if player is not None:
				self._send_lobby(player)

	def join(self, user):
		if self.status != STATUS_LOBBY:
			raise GameException('this game already started')
		empty_slot_idx = self._find_empty_slot()
		if empty_slot_idx is None:
			raise GameException('this game is full')

		player = GamePlayer(user, self, idx=empty_slot_idx)
		self.players[empty_slot_idx] = player
		user.game_player = player
		self._broadcast_lobby()

		if self.is_full():
			self.start_round(sio)

	def join_as(self, user, player_name):
		player = None
		for p in self.players:
			if p.user.name == player_name:
				player = p
				break
		if player is None:
			raise GameException('no player named %s found in this game' % player_name)
		player.user = user
		user.game_player = player
		if player.listener is not None:
			player.listener.send_state(self.round)

	def add_observer(self, user):
		player = GamePlayer(user, self, observer=True)
		user.game_player = player
		self.observers[user.sid] = player
		if self.round is not None:
			player.listener = server_utils.ForwardToGamePlayer(sio, player)
			self.round.add_listener(player.listener)
		self._send_lobby(player)

	def is_full(self):
		for player in self.players:
			if player is None:
				return False
		return True

	def set_ready(self, player):
		if self.status != STATUS_SCORE:
			raise GameException('the game is not in scoring')
		player.ready = True

	def start_round(self, sio):
		if self.status == STATUS_ROUND:
			raise GameException('this game already started')
		listeners = []
		for player in self.players + self.observers.values():
			player.listener = server_utils.ForwardToGamePlayer(sio, player)
			listeners.append(player.listener)
		self.round = model.Round(len(self.players),
		                         listeners=[self, server_utils.TimedActionListener(args.speed)] + listeners,
								 deck_name=args.deck_name)

	def ended(self, r, player_scores, next_player):
		for player in self.players + self.observers.values():
			player.ready = False
			player.listener = None
		self.round = None
		self.status = STATUS_SCORE

	def player_left(self, player):
		if player.listener is not None:
			self.round.remove_listener(player.listener)
			player.listener = None
		if player.observer:
			del self.observers[player.user.sid]
		self._broadcast_lobby()

	@property
	def list_dict(self):
		num_players = sum([1 for player in self.players if player is not None])
		return {
			'id': self.id,
			'name': self.name,
			'occupied': num_players,
			'total': len(self.players),
		}

	def lobby_dict(self, playerIndex):
		player_dicts = []
		for player in self.players:
			if player is None:
				player_dicts.append({
					'name': 'Empty',
					'left': False,
				})
			else:
				player_dicts.append({
					'name': player.user.name,
					'left': player.user.left,
				})
		return {
			'players': player_dicts,
			'playerIndex': playerIndex,
		}

class GameException(Exception):
	pass

sio = socketio.Server()
app = Flask(__name__)

users = {}
games = {}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
	if path == '':
		path = 'index.html'
	return send_from_directory('../web/', path)

@sio.on('connect')
def on_connect(sid, environ):
	print('[server] user {} connected'.format(sid))
	if args.debug:
		sio.emit('debug')
		if len(users) < 4:
			register(sid, 'player{}'.format(len(users)+1))
			if len(games) > 0:
				join(sid, list(games.keys())[0])
			else:
				create(sid, 'debug game', 4)

@sio.on('register')
def register(sid, name):
	if sid in users:
		sio.emit('error', 'you are already registered', room=sid)
		return
	users[sid] = User(sid, name)
	sio.emit('register', name, sid)
	if args.debug and len(users) > 4:
		join_as(sid, name)

@sio.on('game_list')
def game_list(sid):
	l = []
	for game in games.values():
		if game.status == STATUS_LOBBY:
			l.append(game.list_dict)
	sio.emit('game_list', l, room=sid)

def process_user(func):
	def func_wrapper(sid, *args):
		if sid not in users:
			sio.emit('error', 'you did not register', room=sid)
			return
		func(users[sid], *args)
	return func_wrapper

@sio.on('create')
@process_user
def create(user, name, num_players):
	game_id = str(uuid.uuid4())
	game = Game(sio, game_id, name, num_players)
	games[game_id] = game
	game.join(user)

def do_join(user, game_id, player_idx=None):
	if game_id not in games:
		sio.emit('error', 'no such game', room=user.sid)
		return
	game = games[game_id]
	try:
		if player_idx is not None:
			print('[server] user {} re-joining game {}, idx={}'.format(user.sid, game_id, player_idx))
			game.join_as(user, player_idx)
		elif game.is_full():
			print('[server] user {} joining game {} as an observer'.format(user.sid, game_id))
			game.add_observer(user)
		else:
			print('[server] user {} joining game {}'.format(user.sid, game_id))
			game.join(user)
	except GameException as e:
		print('[server] user {} join error: {}'.format(user.sid, e.message))
		sio.emit('error', e.message, room=user.sid)

@sio.on('join')
@process_user
def join(user, game_id):
	do_join(user, game_id)

@sio.on('join_as')
@process_user
def join_as(user, player_idx):
	do_join(user, list(games.keys())[0], player_idx=player_idx)

def process_game_player(func):
	def func_wrapper(user, *args):
		if user.game_player is None:
			sio.emit('error', 'you are not currently in a game', room=user.sid)
			return
		elif user.game_player.observer:
			sio.emit('error', 'you are an observer', room=user.sid)
			return
		func(user.game_player, *args)
	return func_wrapper

def process_round(func):
	def func_wrapper(game_player, *args):
		if game_player.game.round is None:
			sio.emit('error', 'the round has not started yet', room=game_player.user.sid)
			return
		try:
			func(game_player.game.round, game_player.idx, *args)
		except model.RoundException as e:
			sio.emit('error', e.message, room=game_player.user.sid)
	return func_wrapper

def process_user_round(func):
	return process_user(process_game_player(process_round(func)))

@sio.on('round_declare')
@process_user_round
def round_declare(r, player, cards):
	cards = [model.card_from_dict(card) for card in cards]
	print('declaring {} for {}'.format(cards, player))
	r.declare(player, cards)

@sio.on('round_set_bottom')
@process_user_round
def round_set_bottom(r, player, cards):
	cards = [model.card_from_dict(card) for card in cards]
	print('setting bottom to {}'.format(cards))
	r.set_bottom(player, cards)

@sio.on('round_play')
@process_user_round
def round_play(r, player, cards):
	cards = [model.card_from_dict(card) for card in cards]
	print('player {} playing {}'.format(player, cards))
	r.play(player, cards)

@sio.on('disconnect')
def on_disconnect(sid):
	if sid not in users:
		return
	print('[server] user {} disconnected'.format(sid))
	user = users[sid]
	user.left = True
	del users[sid]
	if user.game_player is not None:
		user.game_player.game.player_left(user.game_player)

if __name__ == '__main__':
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
