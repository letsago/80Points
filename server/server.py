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

class GamePlayer(object):
	def __init__(self, game, observer=False, idx=None, user=None):
		self.game = game
		self.observer = observer
		self.idx = idx
		self.ready = False
		self.listener = None

		# we record name of self.user as an additional field so that we can display the names
		#  of users who left the game while the game was in progress
		# if a player re-joins as a player who left, the name is updated to reflect the new
		#  player's name
		# if a player leaves before the game starts, we do not retain their name
		self.name = None
		self.set_user(user)

	def set_user(self, user):
		self.user = user

		if user is not None:
			self.name = user.name

	@property
	def empty(self):
		return self.user is None and self.name is None

	@property
	def left(self):
		return self.user is None and self.name is not None

	@property
	def slot_name(self):
		if self.name is None:
			return 'Empty'
		return self.name

	@property
	def slot_dict(self):
		return {
			'name': self.slot_name,
			'left': self.left,
		}

STATUS_LOBBY = 'lobby'
STATUS_ROUND = 'round'
STATUS_SCORE = 'score'

class Game(model.RoundListener):
	def __init__(self, sio, id, name, num_players):
		self.sio = sio
		self.id = id
		self.name = name
		self.status = STATUS_LOBBY
		self.players = [GamePlayer(self, idx=idx) for idx in range(num_players)]
		self.round = None

		# players observing this game, sid->GamePlayer
		self.observers = {}

	def _log(self, msg):
		print('[game {}-{}] '.format(self.id, self.name) + msg)

	# Return index of an empty slot, or None if no such slot.
	def _find_empty_slot(self):
		for i in range(len(self.players)):
			if self.players[i].empty:
				return i
		return None

	def _send_lobby(self, player):
		if player.user is None:
			return
		self.sio.emit('lobby', self.lobby_dict(player.idx), room=player.user.sid)

	def _broadcast_lobby(self):
		for player in self.players + self.observers.values():
			self._send_lobby(player)

	def _ensure_listener(self, player):
		# make sure player is listening on the round
		if self.round is None:
			return
		elif player.listener is not None:
			return

		player.listener = server_utils.ForwardToGamePlayer(sio, player)
		self.round.add_listener(player.listener)
		player.listener.send_state(self.round)

	# Join while game is in lobby (before game starts) in the first empty slot.
	def join(self, user):
		empty_slot_idx = self._find_empty_slot()
		if empty_slot_idx is None:
			raise GameException('this game is full')
		self.join_as(user, empty_slot_idx)

	# Join the game at a specific player index.
	def join_as(self, user, player_idx):
		if player_idx < 0 or player_idx >= len(self.players):
			raise GameException('slot {} is not valid'.format(player_idx))
		player = self.players[player_idx]
		if player.user is not None:
			raise GameException('slot {} is neither empty nor left'.format(player_idx))
		self._log('user {} joining in slot {}'.format(user.name, player_idx))
		player.set_user(user)
		user.game_player = player
		self._ensure_listener(player)
		self._broadcast_lobby()

		if self.status == STATUS_LOBBY and self.is_full():
			self.start_round(self.sio)

	def add_observer(self, user):
		self._log('user {} joining as an observer'.format(user.name))
		player = GamePlayer(self, observer=True, user=user)
		user.game_player = player
		self.observers[user.sid] = player
		if self.round is not None:
			player.listener = server_utils.ForwardToGamePlayer(sio, player)
			self.round.add_listener(player.listener)
		self._send_lobby(player)

	def is_full(self):
		if self.status != STATUS_LOBBY:
			return True
		for player in self.players:
			if player.user is None:
				return False
		return True

	def set_ready(self, player):
		if self.status != STATUS_SCORE:
			raise GameException('the game is not in scoring')
		player.ready = True

	def start_round(self, sio):
		if self.status == STATUS_ROUND:
			raise GameException('this game already started')
		self.status = STATUS_ROUND
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
		if player.observer:
			del self.observers[player.user.sid]
		if player.listener is not None:
			self.round.remove_listener(player.listener)
			player.listener = None
		player.user = None
		if self.status == STATUS_LOBBY:
			player.name = None
		self._broadcast_lobby()

	@property
	def list_dict(self):
		num_players = sum([1 for player in self.players if not player.empty])
		return {
			'id': self.id,
			'name': self.name,
			'occupied': num_players,
			'total': len(self.players),
		}

	def lobby_dict(self, playerIndex):
		player_dicts = [player.slot_dict for player in self.players]
		return {
			'game_id': self.id,
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
	print('[server] user {} registered as {}'.format(sid, name))
	users[sid] = User(sid, name)
	sio.emit('register', name, sid)
	if args.debug and len(users) > 4:
		join(sid, list(games.keys())[0])

@sio.on('game_list')
def game_list(sid):
	l = []
	for game in games.values():
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
	if user.game_player is not None:
		user.game_player.game.player_left(user.game_player)
		user.game_player = None
	game = games[game_id]
	try:
		if player_idx is not None:
			game.join_as(user, player_idx)
		elif game.is_full():
			game.add_observer(user)
		else:
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
def join_as(user, game_id, player_idx):
	do_join(user, game_id, player_idx=player_idx)

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
	try:
		r.play(player, cards)
	except model.RoundException:
		sio.emit('play_invalid')

@sio.on('disconnect')
def on_disconnect(sid):
	if sid not in users:
		return
	print('[server] user {} disconnected'.format(sid))
	user = users[sid]
	del users[sid]
	if user.game_player is not None:
		user.game_player.game.player_left(user.game_player)

if __name__ == '__main__':
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
