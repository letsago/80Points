from model import Card
import collections
import functools

SUIT_LOWEST = 0
SUIT_TRICK = 1
SUIT_TRUMP = 2

@functools.total_ordering
class Tractor(object):
	'''Tractor represents a structured set of cards.'''

	def __init__(self, rank, length, card, suit_type):
		# Rank refers to how many cards there are of each number.
		self.rank = rank
		# Length refers to how long the tractor is, i.e. how many consecutive numbers there are.
		self.length = length
		# Card refers to the lowest card in the tractor, which can be used to compare two
		# tractors of the same rank and length.
		self.card = card
		# Suit type is the kind of suit the tractor is. There are three kinds of suits: trump,
		# trick, and lowest. The trick suit is the suit played in the first play of the trick.
		# The lowest suit is any suit that is not the trump or trick suit.
		self.suit_type = suit_type

	def __str__(self):
		return '(r: %s l: %s c: %s)' % (self.rank, self.length, self.card)

	def __repr__(self):
		return self.__str__()

	def __eq__(self, other):
		'''
		Returns whether self and other are the same tractor.
		'''
		return self.rank == other.rank and self.length == other.length and self.card == other.card

	def __lt__(self, other):
		'''
		Returns whether self is less than other.
		'''
		if self.rank != other.rank:
			return self.rank < other.rank
		if self.length != other.length:
			return self.length < other.length
		if self.suit_type != other.suit_type:
			return self.suit_type < other.suit_type
		return self.card < other.card

def card_to_suit_type(card, trick_suit, trump_suit):
	if card.suit == 'joker' or card.suit == trump_suit:
		return SUIT_TRUMP
	if card.suit == trick_suit:
		return SUIT_TRICK
	return SUIT_LOWEST

def cards_to_tractors(cards, trick_suit, trump_suit):
	counter = collections.Counter(cards)
	tractors = []
	for card, count in counter.items():
		suit_type = card_to_suit_type(card, trick_suit, trump_suit)
		tractors.append(Tractor(count, 1, card, suit_type))
	tractors = sorted(tractors, reverse=True)
	i = 0
	while i < len(tractors) - 1:
		tractor1, tractor2 = tractors[i], tractors[i+1]
		if tractor1.rank == tractor2.rank and tractor1.suit_type == tractor2.suit_type and abs(tractor1.card.index() - tractor2.card.index()) == 1:
			tractors[i] = Tractor(tractor1.rank, tractor1.length + tractor2.length, tractor2.card, tractor1.suit_type)
			del tractors[i+1]
		else:
			i += 1
	return tractors

@functools.total_ordering
class Flush(object):
	'''Flush represents a single person's play in a trick.'''

	def __init__(self, cards, trick_suit, trump_suit):
		self.tractors = cards_to_tractors(cards, trick_suit, trump_suit)

	def __eq__(self, other):
		'''
		Returns whether self and other are the same flush.
		'''
		if len(self.tractors) != len(other.tractors):
			return False
		for i, tractor in self.tractors:
			if tractor != other.tractors[i]:
				return False
		return True

	def __lt__(self, other):
		'''
		Returns whether self is less than other.
		'''
		for i, tractor in self.tractors:
			if tractor == other.tractors[i]:
				continue 
			return tractor < other.tractors[i]