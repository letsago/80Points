class Card(object):
	def __init__(self, suit, value):
		'''
		Creates a new card with the specified suit and value.
		'''
		self.suit = suit
		self.value = value

	def __eq__(self, other):
		'''
		Returns whether self and other are the same card.
		'''
		return self.suit == other.suit and self.value == other.value

	def __ne__(self, other):
		return not self.__eq__(other)

def create_deck(num_decks):
	'''
	Return a list of cards for the specified number of decks.
	'''

	suit = ['d', 'h', 's', 'c']
	number = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
	one_deck = [Card('joker', 'big'), Card('joker', 'small')]
	for n in range(len(suit)):
		for m in range(len(number)):
			one_deck.append(Card(suit[n], number[m]))
	total_decks = num_decks * one_deck
	return total_decks

class RoundState(object):
	def __init__(self, num_players):
		'''
		Creates a new RoundState for num_players players.
		'''
		raise NotImplementedError

	def deal_card_to_player(self, player, card):
		'''
		Add the card to the player's hand.
		'''
		raise NotImplementedError

	def get_player_hand(self, player):
		'''
		Returns a list of cards in the player's hand.
		'''
		raise NotImplementedError

	def get_board(self):
		'''
		Returns the cards that have been played by each player in the current play.
		'''
		raise NotImplementedError

	def get_player_view(self, player):
		'''
		Returns a view of the state from the perspective of the given player.
		'''
		raise NotImplementedError

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
		raise NotImplementedError

	def add_listener(self, listener):
		'''
		Begin passing events on this Round to the provided RoundListener.
		'''
		raise NotImplementedError

	def tick(self):
		'''
		Execute the next timed action (e.g. dealing cards).
		'''
		raise NotImplementedError

	def declare(self, player, cards):
		'''
		Declare the cards.
		'''
		raise NotImplementedError

	def play(self, player, cards):
		'''
		Play the cards.
		'''
		raise NotImplementedError

	def set_bottom(self, player, cards):
		'''
		Set the bottom.
		'''
		raise NotImplementedError

	def get_state(self):
		'''
		Returns the current RoundState of this Round.
		'''
		raise NotImplementedError
