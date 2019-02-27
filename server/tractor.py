from model import Card
import collections
import functools

SUIT_LOWEST = 0
SUIT_TRICK = 1
SUIT_TRUMP = 2

@functools.total_ordering
class Tractor(object):
	'''Tractor represents a structured set of cards.'''

	def __init__(self, rank, length, power, suit_type):
		# Rank refers to how many cards there are of each number.
		self.rank = rank
		# Length refers to how long the tractor is, i.e. how many consecutive numbers there are.
		self.length = length
		# Power is the suit power of the lowest card in the tractor, which can be used to
		# compare two tractors of the same rank and length.
		self.power = power
		# Suit type is the kind of suit the tractor is. There are three kinds of suits: trump,
		# trick, and lowest. The trick suit is the suit played in the first play of the trick.
		# The lowest suit is any suit that is not the trump or trick suit.
		self.suit_type = suit_type

	def __str__(self):
		return '(r: %s l: %s p: %s t: %d)' % (self.rank, self.length, self.power, self.suit_type)

	def __repr__(self):
		return self.__str__()

	def __eq__(self, other):
		'''
		Returns whether self and other are the same tractor.
		'''
		return self.rank == other.rank and self.length == other.length and self.power == other.power and self.suit_type == other.suit_type

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
		return self.power < other.power

def card_to_suit_type(card, trick_suit, trump_card):
	if card.is_trump(trump_card):
		return SUIT_TRUMP
	if card.suit == trick_suit:
		return SUIT_TRICK
	return SUIT_LOWEST

def match_form(tractors, target_form):
	'''
	Recursively finds a length/rank matching between tractors and target_form.
	Returns the adjusted Tractors, or None if no match was found.
	'''
	if len(tractors) == 0 and len(target_form) == 0:
		return []
	elif len(tractors) == 0 or len(target_form) == 0:
		return None

	# try matching the first tractor in target_form with every tractor in tractors
	# then, we recursively match the remainder (brute force)
	tractor = target_form[0]
	for i in range(len(tractors)):
		other = tractors[i]
		if other.rank < tractor.rank or other.length < tractor.length:
			continue

		# compute remainder tractor(s) after matching other with tractor
		other_match_tractor = Tractor(tractor.rank, tractor.length, other.power, other.suit_type)
		other_minus_tractor = []
		if other.rank > tractor.rank:
			# example: tractor={2,2,3,3}
			# if other is {4,4,4,5,5,5}, remainder is {4,5}
			# if other is {4,4,4,5,5,5,6,6,6}, remainder is {4,5,6,6,6}
			other_minus_tractor.append(Tractor(other.rank - tractor.rank, tractor.length, other.power, other.suit_type))
			if other.length > tractor.length:
				# TODO(workitem0026): we actually need to adjust other.power here if we want to stay consistent, but it might not matter
				other_minus_tractor.append(Tractor(other.rank, other.length - tractor.length, other.power, other.suit_type))
		elif other.length > tractor.length:
			other_minus_tractor.append(Tractor(other.rank, other.length - tractor.length, other.power, other.suit_type))

		# check if remainders match
		remainder_tractors = tractors[:i] + other_minus_tractor + tractors[i+1:]
		remainder_matched = match_form(remainder_tractors, target_form[1:])
		if remainder_matched is not None:
			return remainder_matched + [other_match_tractor]

	# nothing matched, so we failed
	return None

def cards_to_tractors(cards, trick_suit, trump_card, target_form=None):
	"""
	Returns a list of Tractors corresponding to a set of played Cards.
	cards: an iterable of played Cards
	trick_suit: the suit played by the first player in this trick
	trump_card: card defining the trump suit/value of this round

	target_form: a list of Tractors; the rank and length of returned tractors must
		match the rank and length of tractors in target_form. We return None if
		there is no way to match.
	"""
	# group equal cards into length 1 Tractors
	counter = collections.Counter(cards)
	tractors = []
	for card, count in counter.items():
		suit_type = card_to_suit_type(card, trick_suit, trump_card)
		tractors.append(Tractor(count, 1, card.suit_power(trump_card), suit_type))
	tractors = sorted(tractors, reverse=True)

	# merge consecutive rank > 1, length 1 Tractors of the same rank into multi-length Tractors
	i = 0
	while i < len(tractors) - 1:
		tractor1, tractor2 = tractors[i], tractors[i+1]
		if tractor1.rank > 1 and tractor1.rank == tractor2.rank and tractor1.suit_type == tractor2.suit_type and abs(tractor1.power - tractor2.power) == 1:
			assert tractor2.length == 1
			tractors[i] = Tractor(tractor1.rank, tractor1.length + tractor2.length, tractor2.power, tractor1.suit_type)
			del tractors[i+1]
		else:
			i += 1

	# sorting is necessary after merging so that tractors are guaranteed to be 
	# sorted by rank, length, suit_type, and then power in that priority order
	# that way, it will make play validation easier as the tractors will already be sorted based on play priority order
	tractors = sorted(tractors, reverse=True)
	
	if target_form is not None:
		# try to adjust tractors to match target_form
		tractors = match_form(tractors, target_form)

	return tractors

def get_all_multirank_tractor_subcombinations(tractors):
	'''
	Given same suit_type tractors input, returns a list of all tractor subcombination rank > 1 and length > 0 plays.
	eg. (8,8,9,9,10,10) -> (8,8,9,9,10,10), (8,8,9,9), (9,9,10,10), (8,8), (9,9), (10,10). 
	Tractor output suit type is asserted to be equal to tractor input suit type. 

	Args:
		tractors: Tractor []
	Returns:
		Tractor []
	'''
	all_subcombinations = []
	for tractor in tractors:
		for new_rank in range(tractor.rank, 1, -1):
			for new_length in range(tractor.length, 0, -1):
				# eg. given (2,2,3,3,4,4) where tractor.length == 3, 
				# when new_length == 2, valid tractors are (2,2,3,3) and (3,3,4,4),
				# in this case, max_tractor_power_increment == 2 
				# as there are now 2 valid tractor powers of rank 2, length 2 
				max_tractor_power_increment = tractor.length - new_length + 1
				for i in range(max_tractor_power_increment):
					new_tractor_combination = Tractor(new_rank, new_length, tractor.power + i, tractor.suit_type)
					if all_subcombinations:
						assert all_subcombinations[-1].suit_type == new_tractor_combination.suit_type
					all_subcombinations.append(new_tractor_combination)
	return all_subcombinations		

@functools.total_ordering
class Flush(object):
	'''Flush represents a single person's play in a trick.'''

	def __init__(self, tractors):
		self.tractors = tractors

	def __eq__(self, other):
		'''
		Returns whether self and other are the same flush.
		'''
		if len(self.tractors) != len(other.tractors):
			return False
		for i, tractor in enumerate(self.tractors):
			if tractor != other.tractors[i]:
				return False
		return True

	def __lt__(self, other):
		'''
		Returns whether self is less than other.
		'''
		for i, tractor in enumerate(self.tractors):
			if tractor == other.tractors[i]:
				continue
			return tractor < other.tractors[i]
		return False
