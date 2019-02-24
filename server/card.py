import itertools

CARD_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_SUITS = ['c', 'd', 'h', 's']

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

	def suit_power(self, trump_card):
		'''
		Returns an integer corresponding to the power of this card in its own suit.
		This power is sequential, suitable for combining tractors.
		It is NOT suitable for display because cards of the trump value that don't
		  match the trump suit are assigned the same power. (For example, if trump
		  is 2C, 2D and 2S have the same power.)
		'''
		# TODO(workitem0029): handle nonconsecutive pairs as valid tractors case
		if not self.is_trump(trump_card):
			return CARD_VALUES.index(self.value)

		# handle trump suit
		# increments of 1 are used to explicitly make clear what the power hierarchy is
		if self.suit == 'joker' and self.value == 'big':
			return len(CARD_VALUES) + 3
		elif self.suit == 'joker' and self.value == 'small':
			return len(CARD_VALUES) + 2
		# TODO(workitem0030): handle trump power level for joker trump round case
		elif self.suit == trump_card.suit and self.value == trump_card.value:
			return len(CARD_VALUES) + 1
		elif self.value == trump_card.value:
			return len(CARD_VALUES)
		else:
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
	