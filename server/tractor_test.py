import unittest
import model
from model import Card
from tractor import *

def Many(suit, value, rank=1, length=1):
	cards = []
	initial = model.CARD_VALUES.index(value)
	for i in range(length):
		cards.extend(rank * [Card(suit, model.CARD_VALUES[initial + i])])
	return cards

def Straight(suit, value, length):
	return Many(suit, value, length=length)

def Double(suit, value):
	return Many(suit, value, rank=2)

class TestTractor(unittest.TestCase):
	def testCardsToTractors(self):
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

	def testCardsToTractorsWithForm(self):
		# trick suit always 'd', trump suit always 's'
		tests = [
			(
				# player1 plays triple, double, double in trick suit
				# player2 plays quadruple, triple in trump suit
				Many('d', '2', rank=3) + Double('d', '4') + Double('d', '6'),
				Many('s', '2', rank=4) + Many('s', '4', rank=3),
				True,
			), (
				# player1 plays triple, double, double in trick suit
				# player2 plays triple, triple, single in trump suit
				Many('d', '2', rank=3) + Double('d', '4') + Double('d', '6'),
				Many('s', '2', rank=3) + Many('s', '4', rank=3) + [Card('s', '6')],
				False,
			), (
				#player1 plays double,double,double; triple,triple; triple in trick suit
				#player2 plays triple,triple,triple; double,double,double in trump suit
				Many('d', '2', rank=2, length=3) + Many('d', '6', rank=3, length=2) + Many('d', '9', rank=3, length=1),
				Many('s', '2', rank=3, length=3) + Many('s', '6', rank=2, length=3),
				True,
			), (
				#player1 plays double,double,double; triple,triple; triple in trick suit
				#player2 plays triple,triple,triple; triple,triple in trump suit
				Many('d', '2', rank=2, length=3) + Many('d', '6', rank=3, length=2) + Many('d', '9', rank=3, length=1),
				Many('s', '2', rank=3, length=3) + Many('s', '6', rank=3, length=2),
				False,
			),
		]

		for test in tests:
			start_cards, cur_cards, want = test
			target_form = cards_to_tractors(start_cards, 'd', 's')
			okay = cards_to_tractors(cur_cards, 'd', 's', target_form=target_form) is not None
			self.assertEqual(okay, want)

	def testCompareFlush(self):
		trick_suit = 's'
		trump_suit = 'h'

		tests = [
			(Double('s', '2'),
			 Double('s', '5')),
			(Double('d', '5'),
			 Double('s', '2')),
			(Double('s', '5'),
			 Double('h', '2')),
			(Double('s', '5') + Double('s', '8'),
			 Double('s', '3') + Double('s', '4')),
		]

		for test in tests:
			lesser_cards, greater_cards = test
			lesser_flush = Flush(cards_to_tractors(lesser_cards, trick_suit, trump_suit))
			greater_flush = Flush(cards_to_tractors(greater_cards, trick_suit, trump_suit))
			self.assertLess(lesser_flush, greater_flush)

if __name__ == '__main__':
	unittest.main()
