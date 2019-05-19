from model import Card, CARD_VALUES

def Many(suit, value, rank=1, length=1):
	cards = []
	initial = CARD_VALUES.index(value)
	for i in range(length):
		cards.extend(rank * [Card(suit, CARD_VALUES[initial + i])])
	return cards

def Straight(suit, value, length):
	return Many(suit, value, length=length)

def Double(suit, value):
	if suit == 'joker':
		return 2 * [Card(suit, value)]
	return Many(suit, value, rank=2)

# Decode a string like '2s 10s As Ad smalljoker' to a list of corresponding cards.
# If s is already a list of cards or None, simply returns s.
def cards_from_str(s):
	if isinstance(s, list):
		return s
	if s is None:
		return s

	cards = []
	parts = s.split(' ')
	explicit_map = {
		'smalljoker': Card('joker', 'small'),
		'bigjoker': Card('joker', 'big'),
	}
	for part in parts:
		if part in explicit_map:
			cards.append(explicit_map[part])
			continue
		suit = part[-1]
		value = part[:-1]
		cards.append(Card(suit, value))
	return cards

def apply_cards_from_str(*args):
	return (cards_from_str(s) for s in args)
