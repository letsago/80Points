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
	def __init__(self, user, game, idx):
		self.user = user
		self.game = game
		self.idx = idx
		self.ready = False
		self.listener = None

STATUS_LOBBY = 'lobby'
STATUS_ROUND = 'round'
STATUS_SCORE = 'score'

class Game(model.RoundListener):
	def __init__(self, id, name, num_players):
		self.id = id
		self.name = name
		self.status = STATUS_LOBBY
		self.players = [None] * num_players
		self.round = None

	def get_player_from_user(self, user):
		for i, player in enumerate(self.players):
			if player.user == user:
				return (i, player)
		return (None, None)

	def join(self, user):
		if self.status != STATUS_LOBBY:
			raise GameException('this game already started')
		for i in range(len(self.players)):
			if self.players[i] is None:
				player = GamePlayer(user, self, i)
				self.players[i] = player
				user.game_player = player
				return
		raise GameException('this game is full')

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

	def is_full(self):
		for player in self.players:
			if player is None:
				return False
		return True

	def set_ready(self, user):
		if self.status != STATUS_SCORE:
			raise GameException('the game is not in scoring')
		idx, player = self.get_player_from_user(user)
		if player is None:
			raise GameException('you are not in this game')
		player.ready = True

	def start_round(self, sio):
		if self.status == STATUS_ROUND:
			raise GameException('this game already started')
		self.listeners = []
		for player in self.players:
			player.listener = server_utils.ForwardToGamePlayer(sio, player)
			self.listeners.append(player.listener)
		self.round = model.Round(len(self.players), 
		                         listeners=[self, server_utils.TimedActionListener(args.speed)] + self.listeners,
								 deck_name=args.deck_name)

	def ended(self, r, player_scores, next_player):
		for player in self.players:
			player.ready = False
			player.listener = None
		self.round = None
		self.status = STATUS_SCORE

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
		names = []
		for player in self.players:
			if player is None:
				names.append('Empty')
			else:
				names.append(player.user.name)
		return {
			'names': names,
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
	game = Game(game_id, name, num_players)
	games[game_id] = game
	game.join(user)
	sio.emit('lobby', game.lobby_dict(0), room=user.sid)

def do_join(user, game_id, player_name=None):
	if game_id not in games:
		sio.emit('error', 'no such game', room=user.sid)
		return
	game = games[game_id]
	try:
		if player_name is None:
			game.join(user)
		else:
			game.join_as(user, player_name)
	except GameException as e:
		sio.emit('error', e.message, room=user.sid)
		return

	for i, player in enumerate(game.players):
		if player is not None:
			sio.emit('lobby', game.lobby_dict(i), room=player.user.sid)

	if player_name is not None:
		return

	if game.is_full():
		game.start_round(sio)

@sio.on('join')
@process_user
def join(user, game_id):
	do_join(user, game_id)

@sio.on('join_as')
@process_user
def join_as(user, player_name):
	do_join(user, list(games.keys())[0], player_name=player_name)

def process_game_player(func):
	def func_wrapper(user, *args):
		if user.game_player is None:
			sio.emit('error', 'you are not currently in a game', room=user.sid)
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

if __name__ == '__main__':
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
