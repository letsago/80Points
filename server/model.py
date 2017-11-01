import itertools
import random

class Card(object):
	def __init__(self, suit, value):
		'''
		Creates a new card with the specified suit and value.
		'''
		self.suit = suit
		self.value = value

	def __str__(self):
		return str(self.value) + str(self.suit)

	def __eq__(self, other):
		'''
		Returns whether self and other are the same card.
		'''
		return self.suit == other.suit and self.value == other.value

	def __ne__(self, other):
		return not self.__eq__(other)

	@property
	def dict(self):
		return {'suit': self.suit, 'value': self.value}

def create_deck(num_decks):
	'''
	Return a list of cards for the specified number of decks.
	'''

	suit = ['d', 'h', 's', 'c']
	number = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
	one_deck = [Card(x[0], x[1]) for x in itertools.product(suit, number)]
	one_deck.extend([Card('joker', 'big'), Card('joker', 'small')])
	total_decks = num_decks * one_deck
	return total_decks

def is_cards_contained_in(cards, hand):
	'''
	Returns whether cards is contained in hand.
	'''
	check_list = hand[:]
	for x in cards:
		if x in check_list:
			check_list.remove(x)
		else:
			return False
	return True

STATUS_DEALING = 0
STATUS_BOTTOM = 1
STATUS_PLAYING = 2

BOTTOM_SIZE = {
	4: 8,
	5: 8,
	6: 6,
}

class Declaration(object):
	def __init__(self, player, cards):
		self.player = player
		self.cards = cards

class RoundState(object):
	def __init__(self, num_players):
		'''
		Creates a new RoundState for num_players players.
		'''
		self.num_players = num_players
		self.deck = create_deck(num_players // 2)
		random.shuffle(self.deck)
		self.status = STATUS_DEALING
		self.turn = 0

		# list of cards in each player's hand
		self.player_hands = [[] for i in range(num_players)]

		# list of cards that each player has placed on the board for the current play
		self.board = [[] for i in range(num_players)]

		# current declared cards
		# for now, we only keep track of the most recent set of cards that have been declared
		# however, this is insufficient to allow defending a previous declaration, so eventually
		#  we will need to keep a history of declarations from different players
		self.declaration = None

		# some cards should form the bottom
		self.bottom = [self.pop_card_from_deck() for i in range(BOTTOM_SIZE[num_players])]

	def pop_card_from_deck(self):
		card = self.deck[-1]
		self.deck = self.deck[:-1]
		return card

	def deal_card_to_player(self, player):
		'''
		Add a card to the player's hand.
		'''
		card = self.pop_card_from_deck()
		self.player_hands[player].append(card)
		return card

	def increment_turn(self):
		self.turn = (self.turn + 1) % self.num_players

	def give_bottom_to_player(self, player):
		bottom_cards = self.bottom
		self.bottom = []
		self.player_hands[player].extend(bottom_cards)
		return bottom_cards

	def remove_cards_from_hand(self, player, cards):
		'''
		Removes the specified cards from the player's hand.
		'''
		for card in cards:
			self.player_hands[player].remove(card)

	def get_player_view(self, player):
		'''
		Returns a view of the state from the perspective of the given player.
		'''
		view = {
			'hand': [card.dict for card in self.player_hands[player]],
			'player_hands': [len(hand) for hand in self.player_hands],
			'turn': self.turn,
			'status': self.status
		}
		view['board'] = []
		for cards in self.board:
			view['board'].append([str(card) for card in cards])
		return view

class RoundListener(object):
	def timed_action(self, r, delay):
		'''
		A timed action should be performed after the specified delay.
		'''
		pass

	def card_dealt(self, r, player, card):
		'''
		The card was dealt to the player.
		'''
		pass

	def player_declared(self, r, player, cards):
		'''
		A player declared the specified cards.
		'''
		pass

	def player_given_bottom(self, r, player, cards):
		'''
		The player was given the cards from the bottom.
		'''
		pass

	def player_set_bottom(self, r, player, cards):
		'''
		The player set the bottom.
		'''
		pass

	def player_played(self, r, player, cards):
		'''
		A player played the specified cards.
		'''
		pass

class Round(object):
	def __init__(self, num_players, listeners=[]):
		'''
		Create a new Round instance.

		Each Round represents one round of tractor.
		'''
		self.state = RoundState(num_players)
		self.listeners = list(listeners)
		self._fire(lambda listener: listener.timed_action(self, 1))

	def add_listener(self, listener):
		'''
		Begin passing events on this Round to the provided RoundListener.
		'''
		self.listeners.append(listener)

	def _fire(self, f):
		for listener in self.listeners:
			f(listener)

	def tick(self):
		'''
		Execute the next timed action (e.g. dealing cards).
		'''
		if self.state.status == STATUS_DEALING:
			if len(self.state.deck) > 0:
				card = self.state.deal_card_to_player(self.state.turn)
				self._fire(lambda listener: listener.card_dealt(self, self.state.turn, card))
				self.state.increment_turn()

				# notify about the next timed action, which is either to deal the
				# next card or to advance to STATUS_BOTTOM
				if len(self.state.deck) > 0:
					self._fire(lambda listener: listener.timed_action(self, 1))
				else:
					self._fire(lambda listener: listener.timed_action(self, 10))
			else:
				# advance to STATUS_BOTTOM by adding the bottom to the player who declared
				# TODO: handle case where no player declared within the time limit
				# TODO: the 10 second time limit above should be shorter if a player has declared
				#  and longer if no player has declared yet
				bottom_player = self.state.declaration.player
				bottom_cards = self.state.give_bottom_to_player(bottom_player)
				self.state.status = STATUS_BOTTOM
				self._fire(lambda listener: listener.player_given_bottom(self, bottom_player, bottom_cards))

	def declare(self, player, cards):
		'''
		Declare the cards.
		'''
		if self.state.status != STATUS_DEALING:
			raise RoundException("the trump suit has already been decided")

		player_hand = self.state.player_hands[player]
		if not is_cards_contained_in(cards, player_hand):
			raise RoundException("invalid cards")

		self.state.declaration = Declaration(player, cards)
		self._fire(lambda listener: listener.player_declared(self, player, cards))

	def play(self, player, cards):
		'''
		Play the cards.
		'''
		raise NotImplementedError

	def set_bottom(self, player, cards):
		'''
		Set the bottom.
		'''
		if self.state.status != STATUS_BOTTOM:
			raise RoundException("the bottom has already been set")
		elif self.state.declaration.player != player:
			raise RoundException("you did not have the bottom")
		elif len(cards) != BOTTOM_SIZE[self.state.num_players]:
			raise RoundException("the bottom must be {} cards".format(BOTTOM_SIZE[self.state_num_players]))

		player_hand = self.state.player_hands[player]
		if not is_cards_contained_in(cards, player_hand):
			raise RoundException("invalid cards")

		self.state.remove_cards_from_hand(player, cards)
		self._fire(lambda listener: listener.player_set_bottom(self, player, cards))

	def get_state(self):
		'''
		Returns the current RoundState of this Round.
		'''
		return self.state

class RoundException(Exception):
	pass
