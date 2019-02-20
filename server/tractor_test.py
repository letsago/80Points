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
	if suit == 'joker':
		return 2 * [Card(suit, value)]
	return Many(suit, value, rank=2)

class TestTractor(unittest.TestCase):
	def testNonJokerTrumpCardsToTractors(self):
		trump_card = Card('s', '8')
		trick_suit = 's'
		tests = [
			# consecutive pairs (s 2, s 2, s 3, s 3)
			(Double('s', '2') + Double('s', '3'),
			 [Tractor(2, 2, Card('s', '2').suit_power(trump_card), SUIT_TRUMP)]),

			# consecutive singles (s 2, s 3, s 4, s 5)
			(Straight('s', '2', 4),
			 [
				Tractor(1, 1, Card('s', '5').suit_power(trump_card), SUIT_TRUMP),
			 	Tractor(1, 1, Card('s', '4').suit_power(trump_card), SUIT_TRUMP),
			 	Tractor(1, 1, Card('s', '3').suit_power(trump_card), SUIT_TRUMP),
			 	Tractor(1, 1, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# single card (s 2)
			([Card('s', '2')],
			 [Tractor(1, 1, Card('s', '2').suit_power(trump_card), SUIT_TRUMP)]),

			# consecutive pairs (s 2, s 2, s 3, s 3) and single card (s 5)
			(Double('s', '2') + Double('s', '3') + [Card('s', '5')],
			 [
				Tractor(2, 2, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
				Tractor(1, 1, Card('s', '5').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# pair (s 2, s 2) and single card (s 3)
			(Double('s', '2') + [Card('s', '3')],
			 [
				Tractor(2, 1, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
				Tractor(1, 1, Card('s', '3').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# consecutive pairs (s 2, s 2, s 3, s 3, s 4, s 4)
			(Double('s', '2') + Double('s', '3') + Double('s', '4'),
			 [Tractor(2, 3, Card('s', '2').suit_power(trump_card), SUIT_TRUMP)]),

			# non-consecutive pairs (s 2, s 2, s 5, s 5, s 9, s 9)
			(Double('s', '2') + Double('s', '5') + Double('s', '9'),
			 [
				Tractor(2, 1, Card('s', '9').suit_power(trump_card), SUIT_TRUMP),
				Tractor(2, 1, Card('s', '5').suit_power(trump_card), SUIT_TRUMP),
				Tractor(2, 1, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# consecutive pairs (s 2, s 2, s 3, s 3), pair (s 9, s 9), single card (big joker) 
			(Double('s', '2') + Double('s', '3') + Double('s', '9') + [Card('joker', 'big')],
			 [
				Tractor(2, 1, Card('s', '9').suit_power(trump_card), SUIT_TRUMP),
				Tractor(2, 2, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
				Tractor(1, 1, Card('joker', 'big').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# consecutive pairs (h 7, h 7, h 9, h 9) since (s 8) is trump
			(Double('h', '7') + Double('h', '9'),
			 [Tractor(2, 2, Card('s', '7').suit_power(trump_card), SUIT_LOWEST)]),

			# consecutive pairs (d 8, d 8, s 8, s 8) since (s 8) is high trump 8 and (d 8) is low trump 8
			(Double('s', '8') + Double('d', '8'),
			 [Tractor(2, 2, Card('d', '8').suit_power(trump_card), SUIT_TRUMP)]),

			# consecutive pairs (s A, s A, h 8, h 8) since (s 8) is trump
			(Double('s', 'A') + Double('h', '8'),
			 [Tractor(2, 2, Card('s', 'A').suit_power(trump_card), SUIT_TRUMP)]),

			# non-consecutive pairs (c 8, c 8, h 8, h 8) since (s 8) is trump
			(Double('c', '8') + Double('h', '8'),
			 [
				Tractor(2, 1, Card('c', '8').suit_power(trump_card), SUIT_TRUMP),				 
				Tractor(2, 1, Card('h', '8').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# consecutive pairs (s 8, s 8, small joker, small joker) since (s 8) is trump
			(Double('s', '8') + Double('joker', 'small'),
			 [
				Tractor(2, 2, Card('s', '8').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# consecutive pairs (small joker, small joker, big joker, big joker)
			(Double('joker', 'big') + Double('joker', 'small'),
			 [
				Tractor(2, 2, Card('joker', 'small').suit_power(trump_card), SUIT_TRUMP),				 
			 ])
		]

		for test in tests:
			test_cards, want = test
			self.assertEqual(cards_to_tractors(test_cards, trick_suit, trump_card), want)
	
	def testJokerTrumpCardsToTractors(self):
		# Card('joker', '8') object represents the trump suit and value, not an actual card
		trump_card = Card('joker', '8')
		trick_suit = 's'
	
		tests = [
			# non-consecutive pairs (c 8, c 8, h 8, h 8) since (joker, 8) is trump
			(Double('c', '8') + Double('h', '8'),
			 [
				Tractor(2, 1, Card('c', '8').suit_power(trump_card), SUIT_TRUMP),				 
				Tractor(2, 1, Card('h', '8').suit_power(trump_card), SUIT_TRUMP),
			 ]),

			# consecutive pairs (c 8, c 8, small joker, small joker) since (joker, 8) is trump
			(Double('c', '8') + Double('joker', 'small'),
			 [
				Tractor(2, 2, Card('c', '8').suit_power(trump_card), SUIT_TRUMP),				 
			 ]),

			# consecutive pairs (d 8, d 8, small joker, small joker) since (joker, 8) is trump
			(Double('d', '8') + Double('joker', 'small'),
			 [
				Tractor(2, 2, Card('d', '8').suit_power(trump_card), SUIT_TRUMP),				 
			 ]),
			
			# consecutive pairs (h 8, h 8, small joker, small joker) since (joker, 8) is trump
			(Double('h', '8') + Double('joker', 'small'),
			 [
				Tractor(2, 2, Card('h', '8').suit_power(trump_card), SUIT_TRUMP),				 
			 ]),

			# consecutive pairs (s 8, s 8, small joker, small joker) since (joker, 8) is trump
			(Double('s', '8') + Double('joker', 'small'),
			 [
				Tractor(2, 2, Card('s', '8').suit_power(trump_card), SUIT_TRUMP),				 
			 ]),
		]

		for test in tests:
			test_cards, want = test
			self.assertEqual(cards_to_tractors(test_cards, trick_suit, trump_card), want)

	def testCardsToTractorsWithForm(self):
		# trick suit always 'd', trump suit always 's'
		trump_card = Card('s', 'A')
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
			target_form = cards_to_tractors(start_cards, 'd', trump_card)
			okay = cards_to_tractors(cur_cards, 'd', trump_card, target_form=target_form) is not None
			self.assertEqual(okay, want)

	def testCompareFlush(self):
		trick_suit = 's'
		trump_card = Card('h', 'A')

		tests = [
			(Double('s', '2'),
			 Double('s', '5')),
			(Double('d', '5'),
			 Double('s', '2')),
			(Double('s', '5'),
			 Double('h', '2')),
			(Double('s', '5') + Double('s', '8'),
			 Double('s', '3') + Double('s', '4')),
			([Card('s', '5'), Card('s', '7'), Card('s', '8')],
			 [Card('s', '9'), Card('s', 'J'), Card('s', 'Q')]),

			# s A is trump due to trump value, should be higher than low trump
			([Card('h', '2')],
			 [Card('s', 'A')]),
		]

		for test in tests:
			lesser_cards, greater_cards = test
			lesser_flush = Flush(cards_to_tractors(lesser_cards, trick_suit, trump_card))
			greater_flush = Flush(cards_to_tractors(greater_cards, trick_suit, trump_card))
			self.assertLess(lesser_flush, greater_flush)

if __name__ == '__main__':
	unittest.main()
