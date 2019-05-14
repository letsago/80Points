import functools
import itertools
import os
import random

CARD_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_SUITS = ['c', 'd', 'h', 's']

def display_sorted(cards, trump_card):
	return sorted(cards, key=lambda card: card.display_index(trump_card))

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

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(str(self))

	def is_trump(self, trump_card):
		'''
		Checks if card is Trump
		'''
		# handles Jokers
		if self.suit == 'joker':
			return True

		# handles Trump value
		if self.value == trump_card.value:
			return True

		# handles Trump suit
		return self.suit == trump_card.suit

	def get_normalized_suit(self, trump_card):
		'''
		Normally returns a card's suit. However, if the card is trump, then this
		function will return a different suit called 'trump'.

		Args:
			trump_card: Card
		Returns:
			string
		'''
		if self.is_trump(trump_card):
			return 'trump'
		return self.suit

	def suit_power(self, trump_card):
		'''
		Returns an integer corresponding to the power of this card in its own suit.
		This power is sequential, suitable for combining tractors.
		It is NOT suitable for display because cards of the trump value that don't
		  match the trump suit are assigned the same power. (For example, if trump
		  is 2C, 2D and 2S have the same power.)
		'''
		if self.suit == 'joker' and self.value == 'big':
			return len(CARD_VALUES) + 2
		elif self.suit == 'joker' and self.value == 'small':
			return len(CARD_VALUES) + 1
		# handles case where joker is trump suit and all trump values are at equal power level
		elif (trump_card.suit == 'joker' or self.suit == trump_card.suit) and self.value == trump_card.value:
			return len(CARD_VALUES)
		# start with len(CARD_VALUES) - 1 due to power level shift caused by trump value's greater priority
		elif self.value == trump_card.value:
			return len(CARD_VALUES) - 1
		# handles nonjoker, nonvalue trump and nontrump power levels
		# note that separate suit_type parameter not shown here gives priority to trump power levels by design
		else:
			# handles power level cases like 2,2,4,4 being tractor if 3 is trump value
			if CARD_VALUES.index(self.value) > CARD_VALUES.index(trump_card.value):
				return CARD_VALUES.index(self.value) - 1
			return CARD_VALUES.index(self.value)

	def display_index(self, trump_card):
		'''
		Returns an integer suitable for sorting cards for display purposes.
		'''
		# multiple of 100 is used by design to guarantee that non-trump card index is lower than any trump index
		if not self.is_trump(trump_card):
			return 100*CARD_SUITS.index(self.suit) + CARD_VALUES.index(self.value)

		# handle trump suit, starting at 1000 (so that it's higher than any non-trump)
		if self.suit == 'joker' and self.value == 'big':
			return 1400
		elif self.suit == 'joker' and self.value == 'small':
			return 1300
		elif self.suit == trump_card.suit and self.value == trump_card.value:
			return 1200
		elif self.value == trump_card.value:
			return 1100 + CARD_SUITS.index(self.suit)
		else:
			return 1000 + CARD_VALUES.index(self.value)

	@property
	def dict(self):
		return {'suit': self.suit, 'value': self.value}

def card_from_dict(d):
	return Card(d['suit'], d['value'])

def create_deck(num_decks):
	'''
	Return a list of cards for the specified number of decks.
	'''

	one_deck = [Card(x[0], x[1]) for x in itertools.product(CARD_SUITS, CARD_VALUES)]
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

def create_deck_from_file(deck_name):
	'''
	Creates a deck from a file found in the testdata directory. The file
	should be under testdata/<deck_name>.txt

	Returns:
		Card []
	'''
	file_name = os.path.join(os.path.dirname(__file__), 'testdata', deck_name + '.txt')
	deck = []
	with open(file_name, 'r') as f:
		for line in f:
			for card in line.split():
				suit, value = card[0], card[1:]
				if suit == 'j':
					suit = 'joker'
				deck.append(Card(suit, value))
	num_players = 4
	num_decks = num_players // 2
	num_cards_in_deck = 54
	num_cards_in_bottom = 8
	assert len(deck) == num_decks * num_cards_in_deck
	num_playing_cards = len(deck) - num_cards_in_bottom
	num_cards_per_hand = num_playing_cards // num_players
	# Reorder the deck so that it matches how the cards will be popped off the deck to
	# deal the hands.
	reordered_deck = list(deck)
	for hand in range(num_players):
		for position in range(num_cards_per_hand):
			# -1 is to make the index 0-based.
			reordered_deck[num_playing_cards - 1 - hand - num_players * position] = deck[num_cards_per_hand*hand+position]
	return reordered_deck

def is_cards_contained_in(cards, hand):
	'''
	Returns whether cards is contained in hand.
	'''
	check_list = list(hand)
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

from tractor import *

class RoundState(object):
	def __init__(self, num_players, deck_name=None):
		'''
		Creates a new RoundState for num_players players.
		'''
		self.num_players = num_players
		if deck_name is None:
			self.deck = create_random_deck(num_players // 2)
		else:
			self.deck = create_deck_from_file(deck_name)
		self.status = STATUS_DEALING
		self.turn = 0
		# Card object that represents the trump suit and value, not an actual card used in play
		self.trump_card = Card(None, '2')
		self.num_decks = num_players // 2
		self.trick_first_player = 0
		self.bottom_player = 0
		self.attacking_players = []

		# points each player has earned
		self.player_points = [0 for i in range(num_players)]

		# list of cards in each player's hand
		self.player_hands = [[] for i in range(num_players)]

		# list of cards that each player has placed on the board for the current trick
		self.board = [[] for i in range(num_players)]

		# history of all declarations
		# to get the most recent declaration, use self.declaration
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

	def at_max_declaration(self):
		'''
		This function determines whether the latest declaration is the
		maximum declaration possible.

		Returns:
			bool
		'''
		if self.declaration is None:
			return False
		if len(self.declaration.cards) != self.num_decks:
			return False
		return self.declaration.cards[0] == Card('joker', 'big')

	def is_declaration_valid(self, player, cards):
		'''
		This function determines whether a declaration is valid based on the
		history of any previous declarations in this round.

		Args:
			player: int
			cards: Card []
		Returns:
			bool
		'''
	 	# Number of cards must be less than or equal to the number of decks and greater than 0.
		if len(cards) > self.num_decks or len(cards) == 0:
			return False
		# Player can't declare with cards they don't have.
		if not is_cards_contained_in(cards, self.player_hands[player]):
			return False
		# All cards must have the same value.
		if len({card.value for card in cards}) != 1:
			return False
		# All cards must have the same suit.
		if len({card.suit for card in cards}) != 1:
			return False
		# All cards must have the same value as the trump card or be a joker.
		for card in cards:
			if card.value != self.trump_card.value and card.suit != 'joker':
				return False
		# A single joker is not allowed.
		if len(cards) == 1 and cards[0].suit == 'joker':
			return False

		# No previous declarations, so this declaration is fine.
		if self.declaration is None:
			return True

		# If there are less cards than the most recent declaration, it's invalid.
		if len(cards) < len(self.declaration.cards):
			return False
		# Otherwise, the rules depend on whether the cards are jokers or not.
		if cards[0].suit != 'joker':
			# Having the same amount to declare is not enough when using trump values.
			if len(cards) == len(self.declaration.cards):
				return False
			# If the player previously declared, they must use the same suit as before.
			for declaration in self.declarations:
				if player == declaration.player and declaration.cards[0].suit != cards[0].suit:
					return False
		# Dealing with jokers.
		else:
			# If the previous suit is not a joker, the player can't overturn themselves.
			if self.declaration.cards[0].suit != 'joker' and player == self.declaration.player:
				return False
			if len(cards) == len(self.declaration.cards):
				# If the current cards are small jokers, then the last declaration must not be jokers.
				if cards[0].value == 'small' and self.declaration.cards[0].suit == 'joker':
					return False
				# If the current cards are big jokers, then the last declaration must not be big jokers.
				if cards[0].value == 'big' and self.declaration.cards[0].value == 'big':
					return False

		return True

	def declare(self, player, cards):
		self.declarations.append(Declaration(player, cards))
		# Putting the cards on the board makes it appear in the UI, which allows
		# the players to see who declared what.
		self.board[player] = cards
		self.trump_card.suit = cards[0].suit

	def give_bottom_to_player(self, player):
		# Set first player to the player who got the bottom.
		# TODO(workitem0023): set first player properly for all following rounds, i.e. not the first round.
		self.set_turn(player)
		bottom_cards = self.bottom
		self.bottom = []
		self.player_hands[player].extend(bottom_cards)
		self.bottom_player = player
		return bottom_cards
	
	def set_attacking_players(self):
		# TODO(workitem0055): insert logic for odd number player games
		# once odd number player games are supported, assert will be removed
		assert(self.num_players % 2 == 0)
		attacking_team = (self.bottom_player + 1) % 2
		num_teams = self.num_players // 2
		self.attacking_players = [i * 2 + attacking_team for i in range(num_teams)]

	def remove_cards_from_hand(self, player, cards):
		'''
		Removes the specified cards from the player's hand.
		'''
		for card in cards:
			self.player_hands[player].remove(card)

	def is_board_full(self):
		return all([len(cards) > 0 for cards in self.board])

	def is_board_empty(self):
		return all([len(cards) == 0 for cards in self.board])

	def clear_board(self):
		for i in range(len(self.board)):
			self.board[i] = []
	
	def get_trick_points(self):
		points = 0
		for cards in self.board:
			for card in cards:
				if card.value == '5':
					points += 5
				if card.value == '10' or card.value == 'K':
					points += 10
		return points

	def determine_winner(self):
		first_player = (self.turn + 1) % self.num_players
		trick_suit = self.board[first_player][0].suit
		if trick_suit == 'joker':
			trick_suit = self.trump_card.suit
		first_tractors = cards_to_tractors(self.board[first_player], trick_suit, self.trump_card)
		winning_player = first_player
		winning_flush = Flush(first_tractors)
		for i in range(self.num_players - 1):
			player = (first_player + i + 1) % self.num_players
			tractors = cards_to_tractors(self.board[player], trick_suit, self.trump_card, target_form=first_tractors)
			if tractors is None:
				continue
			flush = Flush(tractors)
			if flush > winning_flush:
				winning_player = player
				winning_flush = flush
		# update winning player's point count and set turn to be winning player's
		self.player_points[winning_player] += self.get_trick_points()
		self.set_turn(winning_player)
		return winning_player

	def get_player_view(self, player):
		'''
		Returns a view of the state from the perspective of the given player.
		'''
		view = {
			'player': player,
			'player_hands': [len(hand) for hand in self.player_hands],
			'turn': self.turn,
			'status': self.status,
			'trump_value': self.trump_card.value,
			'trump_suit': self.trump_card.suit,
			'bottom_size': BOTTOM_SIZE[self.num_players],
			'player_points': self.player_points,
			'attacking_players': self.attacking_players,
		}

		if player is not None:
			view['hand'] = [card.dict for card in display_sorted(self.player_hands[player], self.trump_card)]
		else:
			view['hand'] = []

		view['board'] = []
		for cards in self.board:
			view['board'].append([card.dict for card in cards])

		if self.declaration is None:
			view['declaration'] = None
		else:
			view['declaration'] = self.declaration.dict

		return view

	def get_suit_tractors_from_hand(self, player, trick_card):
		'''
		This function returns a list of all tractor plays that are of the trick card's
		suit within a specified player's hand. If trick suit is trump then, a list of all
		trump tractor plays within a player's hand will be returned.

		Args:
			player: int
			trick_card: Card
		Returns:
			Tractor []
		'''
		suit_cards = []
		for card in self.player_hands[player]:
			if card.get_normalized_suit(self.trump_card) == trick_card.get_normalized_suit(self.trump_card):
				suit_cards.append(card)
		suit_tractors = cards_to_tractors(suit_cards, trick_card.suit, self.trump_card)
		return suit_tractors

	def is_play_valid(self, player, cards):
		'''
		This function checks if player's cards, aka play, is valid. In order for a play to be valid, the play
		must follow suit and form of the trick's first play. Otherwise, the appropriate form is calculated
		and used to determine whether or not the play is valid given the trick's first play.

		Args:
			player: int 
			cards: Card [] 
		Returns:
			bool
		'''
		play_card_count = len(cards)
		# number of cards must be nonzero
		if play_card_count == 0:
			return False

		# TODO(workitem0028): once flushing feature is added, then multiple tractors is allowed if player wants to flush
		# for now, first play must be one tractor
		if player == self.trick_first_player:
			# need the first card's suit in order to accurately transform cards to tractors if board is empty
			return len(cards_to_tractors(cards, cards[0].suit, self.trump_card)) == 1
		
		first_play = self.board[self.trick_first_player]
		trick_card_count = len(first_play)
				
		# number of cards played must match number of cards in trick
		if play_card_count != trick_card_count:
			return False
		
		# grab trick tractor and player hand trick suit tractor rank and length data
		trick_card = first_play[0]
		trick_tractors = cards_to_tractors(first_play, trick_card.suit, self.trump_card)
		hand_suit_tractors = self.get_suit_tractors_from_hand(player, trick_card)

		# if hand doesn't have any trick suit cards then player can play cards of any suit as long as 
		# play_card_count equals trick_card_count (case already handled above)
		if not hand_suit_tractors:
			return True
		
		trick_data_array = [TractorMetadata(tractor.rank, tractor.length) for tractor in trick_tractors]
		hand_data_array = [TractorMetadata(tractor.rank, tractor.length) for tractor in hand_suit_tractors]
		
		# find hand data (rank, length) that matches trick data, add it to priority_data_array, and update trick_data 
		# and hand_data accordingly by removing that data from both arrays
		priority_data_array = []
		while trick_data_array and hand_data_array:
			i = find_matching_data_index(hand_data_array, trick_data_array[0])
			min_data = get_min_data(trick_data_array[0], hand_data_array[i])
			priority_data_array.append(min_data)
			trick_data_array = update_data_array(trick_data_array, min_data)
			hand_data_array = update_data_array(hand_data_array, min_data)

		# number of played tractors must be at least the number of priority tractors
		play_tractors = cards_to_tractors(cards, trick_card.suit, self.trump_card)
		if len(play_tractors) < len(priority_data_array):
			return False

		trick_suit_type = card_to_suit_type(trick_card, trick_card.suit, self.trump_card)
		# all sorted priority (rank, length) data must match sorted played tractor data by rank, length, and trick suit_type
		for i in range(len(priority_data_array)):
			priority_rank = priority_data_array[i].rank
			priority_length = priority_data_array[i].length
			if play_tractors[i].rank != priority_rank or play_tractors[i].length != priority_length or play_tractors[i].suit_type != trick_suit_type:
				return False

		return True

class RoundListener(object):
	def round_started(self, r):
		'''
		A round has started.
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

	def send_state(self, r):
		'''
		Refresh game state if an action happened that wasn't initiated by a player.
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
	def __init__(self, num_players, listeners=None, deck_name=None):
		'''
		Create a new Round instance.

		Each Round represents one round of tractor.
		'''
		if listeners is None:
			listeners = []
		self.state = RoundState(num_players, deck_name=deck_name)
		self.listeners = list(listeners)
		self._fire(lambda listener: listener.round_started(self))

	def add_listener(self, listener):
		'''
		Begin passing events on this Round to the provided RoundListener.
		'''
		self.listeners.append(listener)

	def remove_listener(self, listener):
		'''
		Stop passing events to the specified RoundListener.
		'''
		self.listeners.remove(listener)

	def _fire(self, f):
		for listener in self.listeners:
			f(listener)
		
	def finalize_declaration(self):
		'''
		Called after the cards are dealt, only when the declaration should be
		finalized, i.e. after any overturn timers or if the declaration is maximum
		possible already.
		'''
		# Someone declared in this case, so we give them the bottom.
		if self.state.declaration is not None:
			bottom_player = self.state.declaration.player
		# No one declared in this case, so we set the trump card suit to 'joker'.
		else:
			# TODO(workitem0023): This should be pre-determined on subsequent rounds.
			bottom_player = 0
			# Add a dummy declaration so that this (and only this) player can set the bottom.
			self.state.declarations.append(Declaration(bottom_player, []))
			self.state.trump_card.suit = 'joker'
		bottom_cards = self.state.give_bottom_to_player(bottom_player)
		self.state.set_attacking_players()
		self.state.status = STATUS_BOTTOM
		self._fire(lambda listener: listener.player_given_bottom(self, bottom_player, bottom_cards))

	def deal_card(self):
		'''
		Deals the next card to the next player.
		'''
		if self.state.status != STATUS_DEALING:
			raise RoundException("the round is not currently in the dealing stage")
		if len(self.state.deck) == 0:
			raise RoundException("no more cards to deal")
		card = self.state.deal_card_to_player(self.state.turn)
		self._fire(lambda listener: listener.card_dealt(self, self.state.turn, card))
		self.state.increment_turn()

	def declare(self, player, cards):
		'''
		Declare the cards.
		'''
		if self.state.status != STATUS_DEALING:
			raise RoundException("the trump suit has already been decided")

		if not self.state.is_declaration_valid(player, cards):
			raise RoundException("invalid declaration")

		self.state.declare(player, cards)
		self._fire(lambda listener: listener.player_declared(self, player, cards))

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

		# if board is empty, including the first play of the round, where board is not previously cleared,
		# then set trick first player to player 
		if self.state.is_board_empty():
			self.state.trick_first_player = player

		# checks if play is invalid
		if not self.state.is_play_valid(player, cards):
			raise RoundException("Invalid play")

		self.state.board[player] = cards
		self.state.remove_cards_from_hand(player, cards)

		# if all players have played, then we need to figure out who won to update the turn
		# otherwise, we can just increment it
		if self.state.is_board_full():
			if len(self.state.player_hands[0]) > 0:
				winner = self.state.determine_winner()
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
		# Clear board to remove any declared cards from the board.
		self.state.clear_board()
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
		'''
		# TODO(workitem0057): Accumulate attacking team's player points and notify listeners about the round result.
		self.state.status = STATUS_ENDED
		player_scores = [0] * self.state.num_players
		player_scores[0] = 1
		self._fire(lambda listener: listener.end(self, player_scores, 0))

class RoundException(Exception):
	pass
