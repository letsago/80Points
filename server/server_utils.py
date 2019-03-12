import eventlet
import model

class TimedActionListener(model.RoundListener):
	def __init__(self, speed):
		self.speed = speed
		self.pending_declaration_finalization = None
	
	def round_started(self, r):
		# Start dealing the cards.
		r.deal_card()

	def card_dealt(self, r, player, card):
		# When there are no more cards we can finalize the declaration.
		if len(r.state.deck) == 0:
			self.finalize_declaration(r)
			return

		# Deal faster if the declaration is maximum possible already.
		delay = 1
		if r.state.declaration is not None and len(r.state.declaration.cards) == r.state.num_decks:
			delay = 0.1
		eventlet.spawn_after(float(delay) / self.speed, r.deal_card)
	
	def player_declared(self, r, player, cards):
		# If there are no more cards in the deck, then we try to finalize
		# declaration. This either resets the overturn timer or finalizes
		# the declaration directly if it's the max possible.
		if len(r.state.deck) == 0:
			self.finalize_declaration(r)

	def finalize_declaration(self, r):
		# If there is already a queued finalization, we should cancel it and reschedule it.
		# For example, this can happen if a person overturns when a finalization is scheduled
		# but has not executed.
		if self.pending_declaration_finalization is not None:
			self.pending_declaration_finalization.cancel()

		# If the declaration is the maximum possible already, we finalize immediately.
		if r.state.declaration is not None and len(r.state.declaration.cards) == r.state.num_decks:
			r.finalize_declaration()
		# Otherwise, we schedule for finalization to happen in the future, to allow for potential
		# overturning / defending even after all the cards are dealt.
		else:
			self.pending_declaration_finalization = eventlet.spawn_after(100.0 / self.speed, r.finalize_declaration)

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
