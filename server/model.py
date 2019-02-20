import functools
import itertools
import random

CARD_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def key_trump(card, trump_suit, trump_value):
	if card.suit == 'joker' and card.value == 'big':
		return 16
	if card.suit == 'joker' and card.value == 'small':
		return 15
	if card.suit == trump_suit and card.value == trump_value:
		return 14
	if card.value == trump_value:
		return 13
	return CARD_VALUES.index(card.value)

def trump_sorted(cards, trump_suit, trump_value):
	trumps = [card for card in cards if card.is_trump(trump_suit, trump_value)]
	non_trumps = sorted([card for card in cards if not card.is_trump(trump_suit, trump_value)])
	return non_trumps + sorted(trumps, key=lambda x: key_trump(x, trump_suit, trump_value))

@functools.total_ordering
class Card(object):
	def __init__(self, suit, value):
		'''
		Creates a new card with the specified suit and value.
		'''
		self.suit = suit
		self.value = value

	def __str__(self):
		return str(self.value) + str(self.suit)

	def __repr__(self):
		return self.__str__()

	def __eq__(self, other):
		'''
		Returns whether self and other are the same card.
		'''
		return self.suit == other.suit and self.value == other.value

	def __lt__(self, other):
		'''
		Returns whether self is less than other.
		'''
		# handles sorting Joker cards
		if self.suit == 'joker' and other.suit == 'joker':
			if self.value == 'big':
				return False
			if other.value == 'big':
				return True
		if self.suit == 'joker':
			return False
		if other.suit == 'joker':
			return True

		# handles sorting all other cards
		if self.suit < other.suit:
			return True
		if self.suit > other.suit:
			return False

		# handles sorting of values in same suit
		return CARD_VALUES.index(self.value) < CARD_VALUES.index(other.value)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(str(self))

	def is_trump(self, trump_suit, trump_value):
		'''
		Checks if card is Trump
		'''
		# handles Jokers
		if self.suit == 'joker':
			return True

		# handles Trump value
		if self.value == trump_value:
			return True

		# handles Trump suit
		return self.suit == trump_suit

	def index(self):
		return CARD_VALUES.index(self.value)

	@property
	def dict(self):
		return {'suit': self.suit, 'value': self.value}

def card_from_dict(d):
	return Card(d['suit'], d['value'])

def create_deck(num_decks):
	'''
	Return a list of cards for the specified number of decks.
	'''

	suit = ['d', 'h', 's', 'c']
	one_deck = [Card(x[0], x[1]) for x in itertools.product(suit, CARD_VALUES)]
	one_deck.extend([Card('joker', 'big'), Card('joker', 'small')])
	total_decks = num_decks * one_deck
	return total_decks

def create_random_deck(num_decks):
	'''
	Returns a random list of cards for the specified number of decks.
	'''
	deck = create_deck(num_decks)
	random.shuffle(deck)
	return deck

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

STATUS_DEALING = 'dealing'
STATUS_BOTTOM = 'bottom'
STATUS_PLAYING = 'playing'
STATUS_ENDED = 'ended'

BOTTOM_SIZE = {
	4: 8,
	5: 8,
	6: 6,
}

class Declaration(object):
	def __init__(self, player, cards):
		self.player = player
		self.cards = cards

	@property
	def dict(self):
		return {
			'player': self.player,
			'cards': [card.dict for card in self.cards],
		}

from tractor import Flush, cards_to_tractors

class RoundState(object):
	def __init__(self, num_players):
		'''
		Creates a new RoundState for num_players players.
		'''
		self.num_players = num_players
		self.deck = create_random_deck(num_players // 2)
		self.status = STATUS_DEALING
		self.turn = 0
		self.trump_value = '2'
		self.trump_suit = None
		self.num_decks = num_players // 2

		# list of cards in each player's hand
		self.player_hands = [[] for i in range(num_players)]

		# list of cards that each player has placed on the board for the current trick
		self.board = [[] for i in range(num_players)]

		# current declared cards
		# for now, we only keep track of the most recent set of cards that have been declared
		# however, this is insufficient to allow defending a previous declaration, so eventually
		#  we will need to keep a history of declarations from different players
		self.declarations = []

		# some cards should form the bottom
		self.bottom = [self.pop_card_from_deck() for i in range(BOTTOM_SIZE[num_players])]

	@property
	def declaration(self):
		if len(self.declarations) == 0:
			return None
		return self.declarations[-1]

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

	def set_turn(self, player):
		self.turn = player

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

	def is_board_full(self):
		return all([len(cards) > 0 for cards in self.board])

	def clear_board(self):
		for i in range(len(self.board)):
			self.board[i] = []

	def determine_winner(self):
		first_player = (self.turn + 1) % self.num_players
		trick_suit = self.board[first_player][0].suit
		if trick_suit == 'joker':
			trick_suit = self.trump_suit
		first_tractors = cards_to_tractors(self.board[first_player], trick_suit, self.trump_suit)
		winning_player = first_player
		winning_flush = Flush(first_tractors)
		for i in range(self.num_players - 1):
			player = (first_player + i + 1) % self.num_players
			tractors = cards_to_tractors(self.board[player], trick_suit, self.trump_suit, target_form=first_tractors)
			if tractors is None:
				continue
			flush = Flush(tractors)
			if flush > winning_flush:
				winning_player = player
				winning_flush = flush
		return winning_player

	def get_player_view(self, player):
		'''
		Returns a view of the state from the perspective of the given player.
		'''
		view = {
			'player': player,
			'hand': [card.dict for card in trump_sorted(self.player_hands[player], self.trump_suit, self.trump_value)],
			'player_hands': [len(hand) for hand in self.player_hands],
			'turn': self.turn,
			'status': self.status,
			'trump_value': self.trump_value,
			'trump_suit': self.trump_suit,
			'bottom_size': BOTTOM_SIZE[self.num_players],
		}

		view['board'] = []
		for cards in self.board:
			view['board'].append([card.dict for card in cards])

		if self.declaration is None:
			view['declaration'] = None
		else:
			view['declaration'] = self.declaration.dict

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

	def ended(self, r, player_scores, next_player):
		'''
		The round ended.

		player_scores is a list of integers indicating how many levels each player gained.
		next_player is the player who should start the next round.
		'''
		pass

class Round(object):
	def __init__(self, num_players, listeners=None):
		'''
		Create a new Round instance.

		Each Round represents one round of tractor.
		'''
		if listeners is None:
			listeners = []
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
				elif self.state.declaration is not None:
					self._fire(lambda listener: listener.timed_action(self, 5))
			elif self.state.declaration is not None:
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

		if len(cards) > self.state.num_decks:
			raise RoundException("invalid number of cards")
		
		if self.state.declaration is not None:
			if len(cards) <= len(self.state.declaration.cards):
				if player != self.state.declarations[0].player:
					raise RoundException("must use more cards than previous declaration")

		self.state.declarations.append(Declaration(player, cards))
		self.state.trump_suit = cards[0].suit
		self._fire(lambda listener: listener.player_declared(self, player, cards))

		if len(self.state.deck) == 0:
			self._fire(lambda listener: listener.timed_action(self, 5))

	def play(self, player, cards):
		'''
		Play the cards.
		'''
		if self.state.status != STATUS_PLAYING:
			raise RoundException("the round is not in progress")
		elif self.state.turn != player:
			raise RoundException("it's not your turn")

		player_hand = self.state.player_hands[player]
		if not is_cards_contained_in(cards, player_hand):
			raise RoundException("invalid cards")

		# if starting new play, clear previous one
		if self.state.is_board_full():
			self.state.clear_board()

		self.state.board[player] = cards
		self.state.remove_cards_from_hand(player, cards)

		# if all players have played, then we need to figure out who won to update the turn
		# otherwise, we can just increment it
		if self.state.is_board_full():
			# TODO...

			if len(self.state.player_hands[0]) > 0:
				winner = self.state.determine_winner()
				self.state.set_turn(winner)
			else:
				self._end()
		else:
			self.state.increment_turn()

		self._fire(lambda listener: listener.player_played(self, player, cards))

	def set_bottom(self, player, cards):
		'''
		Set the bottom.
		'''
		if self.state.status != STATUS_BOTTOM:
			raise RoundException("the bottom has already been set")
		elif self.state.declaration.player != player:
			raise RoundException("you did not have the bottom")
		elif len(cards) != BOTTOM_SIZE[self.state.num_players]:
			raise RoundException("the bottom must be {} cards".format(BOTTOM_SIZE[self.state.num_players]))

		player_hand = self.state.player_hands[player]
		if not is_cards_contained_in(cards, player_hand):
			raise RoundException("invalid cards")

		self.state.remove_cards_from_hand(player, cards)
		# Set first player to the player who got the bottom.
		# TODO(workitem0023): set first player properly for all following rounds, i.e. not the first round.
		self.state.set_turn(player)
		self.state.status = STATUS_PLAYING
		self._fire(lambda listener: listener.player_set_bottom(self, player, cards))

	def get_state(self):
		'''
		Returns the current RoundState of this Round.
		'''
		return self.state

	def _end(self):
		'''
		Called after the last trick is finished.

		We should accumulate points and then notify listeners about the result
		of this round.
		'''
		self.state.status = STATUS_ENDED
		player_scores = [0] * self.state.num_players
		player_scores[0] = 1
		self._fire(lambda listener: listener.end(self, player_scores, 0))

class RoundException(Exception):
	pass
