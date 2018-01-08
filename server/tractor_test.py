import unittest
import model
from model import Card
from tractor import *

def Straight(suit, value, length):
	cards = []
	initial = model.CARD_VALUES.index(value)
	for i in range(length):
		cards.append(Card(suit, model.CARD_VALUES[initial + i]))
	return cards

def Double(suit, value):
	return 2 * [Card(suit, value)] 

class TestTractor(unittest.TestCase):
	def testCardsToTractors(self):
		ace = Card('s', 'A')
		tests = [
			(Double('s', '2') + Double('s', '3'),
			 [Tractor(2, 2, Card('s', '2'), SUIT_LOWEST)]),
			(Straight('s', '2', 4),
			 [Tractor(1, 4, Card('s', '2'), SUIT_LOWEST)]),
			([Card('s', '2')],
			 [Tractor(1, 1, Card('s', '2'), SUIT_LOWEST)]),
			(Double('s', '2') + Double('s', '3') + [Card('s', '5')],
			 [Tractor(2, 2, Card('s', '2'), SUIT_LOWEST), Tractor(1, 1, Card('s', '5'), SUIT_LOWEST)]),
			(Double('s', '2') + [Card('s', '3')],
			 [Tractor(2, 1, Card('s', '2'), SUIT_LOWEST), Tractor(1, 1, Card('s', '3'), SUIT_LOWEST)]),
			(Double('s', '2') + Double('s', '3') + [Card('s', '4')],
			 [Tractor(2, 2, Card('s', '2'), SUIT_LOWEST), Tractor(1, 1, Card('s', '4'), SUIT_LOWEST)]),
		]
		        
		for test in tests:
			test_cards, want = test
			self.assertEqual(cards_to_tractors(test_cards, 's', 's'), want)
	

if __name__ == '__main__':
	unittest.main()