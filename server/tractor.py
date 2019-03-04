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
	target_tractor = target_form[0]
	for i in range(len(tractors)):
		other = tractors[i]
		if other.rank < target_tractor.rank or other.length < target_tractor.length:
			continue

		# compute remainder tractor(s) after matching other with target_tractor
		other_match_tractor = Tractor(target_tractor.rank, target_tractor.length, other.power, other.suit_type)
		other_minus_tractor = []
		if other.rank > target_tractor.rank:
			# example: target_tractor={2,2,3,3}
			# if other is {4,4,4,5,5,5}, remainder is {4,5}
			# if other is {4,4,4,5,5,5,6,6,6}, remainder is {4,5,6,6,6}
			other_minus_tractor.append(Tractor(other.rank - target_tractor.rank, target_tractor.length, other.power, other.suit_type))
			if other.length > target_tractor.length:
				other_minus_tractor.append(Tractor(other.rank, other.length - target_tractor.length, other.power + target_tractor.length, other.suit_type))
		elif other.length > target_tractor.length:
			other_minus_tractor.append(Tractor(other.rank, other.length - target_tractor.length, other.power, other.suit_type))

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

class TractorMetadata(object):
	'''
	TractorMetadata represents only the rank and length of a particular tractor play.
	This object is primarily used in play validation where rank and length are most relevant to consider.
	'''
	
	def __init__(self, rank, length):
		self.rank = rank
		self.length = length
	
	def __str__(self):
		return '(r: %s l: %s)' % (self.rank, self.length)

	def __repr__(self):
		return self.__str__()
	
	def __eq__(self, other):
		'''
		Returns whether self and other are equal.
		'''
		return self.rank == other.rank and self.length == other.length

	def __lt__(self, other):
		'''
		Returns whether self is less than other.
		'''
		if self.rank != other.rank:
			return self.rank < other.rank
		return self.length < other.length
	
def find_matching_data_index(data_array, target_data):
	'''
	Returns the index to the first data from a reverse sorted data array corresponding to at least a target 
	data's rank and length. If data is not found, then by default the first index will be returned 
	as it corresponds with max data within the reverse sorted data array input. This function is used in both
	update_data_array, where it is guaranteed that matching data index is found, and in the is_play_valid function,
	where it is not guaranteed that matching data index is found.

	Args:
		data_array: TractorMetadata []
		target_data: TractorMetadata
	
	Returns:
		int
	'''
	for i, data in enumerate(data_array):
		# succeeds in finding matching data
		if data.rank >= target_data.rank and data.length >= target_data.length:
			return i
	# fails to find matching data so defaults to first index of data_array, which corresponds to max data, 
	# if data_array is empty, return None
	if data_array:
		return 0
	return None

def update_data_array(data_array, data_to_remove):
	'''
	Returns an updated reverse sorted rank, length data array after removing data_to_remove from 
	data array. This function is used primarily in play validation to accurately update the trick and hand data 
	arrays for subsequent priority play matching. Since you cannot remove greater data from lesser data, assertions 
	are made to check that there exists at least one TractorMetadata in data_array that is greater than data_to_remove. 
	In the play validation logic, before being passed into the function, data_to_remove is calculated to have a rank 
	and length less than at least one element in data_array.

	Args:
		data_array: TractorMetadata []
		data_to_remove: TractorMetadata
	
	Returns:
		TractorMetadata []
	'''
	i = find_matching_data_index(data_array, data_to_remove)
	assert i is not None
	data = data_array[i]
	assert data_to_remove.rank <= data.rank
	assert data_to_remove.length <= data.length

	# case 1: if (2, 1) tractor were to be removed from array tractor (2, 1) then (2, 1) can be directly removed from array
	# case 2: if (2, 1) tractor were to be removed from array tractor (2, 2) then (2, 2) tractor becomes (2, 1)
	# case 3: if (2, 1) tractor were to be removed from array tractor (3, 1) then (3, 1) tractor becomes (1, 1)
	# case 4: if (2, 1) tractor were to be removed from array tractor (3, 2) then (3, 2) tractor becomes (3, 1) and leftover (1, 1) is added
	if data.rank == data_to_remove.rank and data.length == data_to_remove.length:
		data_array.remove(data)
	elif data.rank == data_to_remove.rank:
		data.length = data.length - data_to_remove.length
	elif data.length == data_to_remove.length:
		data.rank = data.rank - data_to_remove.rank
	else:
		data_array.append(TractorMetadata(data.rank, data.length - data_to_remove.length))
		data.rank = data.rank - data_to_remove.rank
		data.length = data_to_remove.length

	# if (1, n), where n > 1, tractor is found at data, then decompose it into n (1, 1) tractors,
	# add them to data_array, and remove the (1, n) tractor
	if len(data_array) > i and data.rank == 1 and data.length > 1:
		data_array += data.length * [TractorMetadata(1, 1)]
		data_array.remove(data)

	return sorted(data_array, reverse=True)

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
