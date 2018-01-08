import eventlet
import model

class TimedActionListener(model.RoundListener):
	def __init__(self, speed):
		self.speed = speed
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
		self.pending_tick = eventlet.spawn_after(float(delay) / self.speed, run_action)

class ForwardToGamePlayer(model.RoundListener):
	'''
	Forwards updates on the Round to a user via sio messages.
	'''

	def __init__(self, sio, game_player):
		self.sio = sio
		self.game_player = game_player

	@property
	def player(self):
		return self.game_player.idx

	@property
	def sid(self):
		return self.game_player.user.sid

	def send_state(self, r):
		view = r.get_state().get_player_view(self.player)
		self.sio.emit('state', view, room=self.sid)

	def card_dealt(self, r, player, card):
		data = {
			'player': player,
		}
		if player == self.player:
			data['card'] = card.dict
		self.sio.emit('card_dealt', data, room=self.sid)
		self.send_state(r)

	def player_declared(self, r, player, cards):
		data = {
			'player': player,
			'cards': [card.dict for card in cards],
		}
		self.sio.emit('player_declared', data, room=self.sid)
		self.send_state(r)

	def player_given_bottom(self, r, player, cards):
		data = {
			'player': player,
		}
		if player == self.player:
			data['cards'] = [card.dict for card in cards]
		self.sio.emit('player_given_bottom', data, room=self.sid)
		self.send_state(r)

	def player_set_bottom(self, r, player, cards):
		data = {
			'player': player,
		}
		if player == self.player:
			data['cards'] = [card.dict for card in cards]
		self.sio.emit('player_set_bottom', data, room=self.sid)
		self.send_state(r)

	def player_played(self, r, player, cards):
		data = {
			'player': player,
			'cards': [card.dict for card in cards],
		}
		self.sio.emit('player_played', data, room=self.sid)
		self.send_state(r)
