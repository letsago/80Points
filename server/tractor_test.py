import unittest
import model
from model import Card
from tractor import *
from parameterized import parameterized_class

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

def tractor_generator(tractors, trump_card):
	return [Tractor(data['rank'], data['length'], data['power_card'].suit_power(trump_card), data['suit_type']) for data in tractors]

@parameterized_class(('test_description', 'test_cards', 's_8_trump_tractor_data', 'joker_8_trump_tractor_data'), [

		(	"same suit consecutive pairs", 
			Double('s', '2') + Double('s', '3'), 
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST}],
		),

		(	"same suit consecutive singles", 
			Straight('s', '2', 4), 
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(	"different suit consecutive value singles", 
			[Card('s', '2'), Card('d', '3')],  
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(	"single", 
			[Card('s', '2')], 
			[{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST}],
		),

		(	"same suit consecutive pairs and single", 
			Double('s', '2') + Double('s', '3') + [Card('s', '5')],
			[
				{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_LOWEST},
			],
		),

		(	"different suit pair and single", 
			Double('s', '2') + [Card('d', '3')],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
			],
		),

		(	"same suit 3 consecutive pairs", 
			Double('s', '2') + Double('s', '3') + Double('s', '4'),
			[{'rank': 2, 'length': 3, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 3, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST}],
		),

		(	"same suit 3 non-consecutive pairs", 
			Double('s', '2') + Double('s', '5') + Double('s', '9'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(	"same suit 2 consecutive pairs, 1 separate pair, 1 single", 
			Double('s', '2') + Double('s', '3') + Double('s', '9') + [Card('joker', 'big')],
			[
				{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('joker', 'big'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('joker', 'big'), 'suit_type': SUIT_TRUMP},
			],
		),

		(	"consecutive joker pair", 
			Double('joker', 'big') + Double('joker', 'small'),
			[{'rank': 2, 'length': 2, 'power_card': Card('joker', 'small'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 2, 'power_card': Card('joker', 'small'), 'suit_type': SUIT_TRUMP}],
		),

		(	"consecutive trump value, joker pair", 
			Double('s', '8') + Double('joker', 'small'),
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
		),

		(	"trump suit 2 non-consecutive pairs", 
			Double('c', '8') + Double('h', '8'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
		),

		(	"different suit 2 consecutive value pairs", 
			Double('c', '2') + Double('h', '3'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '2'), 'suit_type': SUIT_TRICK},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '2'), 'suit_type': SUIT_TRICK},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_LOWEST},
			],
		),

		(	"different suit 2 non-consecutive value pairs", 
			Double('h', '2') + Double('d', '5'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('d', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('d', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"different suit 2 nonconsecutive trump value pairs",
			Double('c', '8') + Double('h', '8'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
		),

		(
			"trump value, joker 2 consecutive pairs",
			Double('s', '8') + Double('joker', 'small'),
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
		),

		(
			"same suit 2 consecutive pairs due to trump value",
			Double('h', '7') + Double('h', '9'),
			[{'rank': 2, 'length': 2, 'power_card': Card('h', '7'), 'suit_type': SUIT_LOWEST}],
			[{'rank': 2, 'length': 2, 'power_card': Card('h', '7'), 'suit_type': SUIT_LOWEST}],
		),

		(
			"s 8 trump - trump value 2 consecutive pairs; joker 8 trump - trump value 2 nonconsecutive pairs",
			Double('s', '8') + Double('d', '8'),
			[{'rank': 2, 'length': 2, 'power_card': Card('d', '8'), 'suit_type': SUIT_TRUMP}],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('d', '8'), 'suit_type': SUIT_TRUMP},
			],
		),

		(
			"s 8 trump - trump suit, trump value 2 consecutive pairs; joker 8 trump - different suit 2 nonconsecutive pairs",
			Double('s', 'A') + Double('h', '8'),
			[{'rank': 2, 'length': 2, 'power_card': Card('s', 'A'), 'suit_type': SUIT_TRUMP}],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('s', 'A'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"s 8 trump - trump value, joker 2 nonconsecutive pairs; joker 8 trump - trump value, joker 2 consecutive pairs",
			Double('c', '8') + Double('joker', 'small'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('joker', 'small'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
			],
			[{'rank': 2, 'length': 2, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP}],
		),
])
class TestCardsToTractors(unittest.TestCase):
	# trick suit always 'c' by design because testing cards_to_tractors output and not comparable tractor strength

	def testNonJokerTrump(self):
		trump_card = Card('s', '8')
		want = tractor_generator(self.s_8_trump_tractor_data, trump_card)
		self.assertEqual(cards_to_tractors(self.test_cards, 'c', trump_card), want)
	
	def testJokerTrump(self):
		# Card('joker', '8') object represents the trump suit and value, not an actual card
		trump_card = Card('joker', '8')
		want = tractor_generator(self.joker_8_trump_tractor_data, trump_card)
		self.assertEqual(cards_to_tractors(self.test_cards, 'c', trump_card), want)

@parameterized_class(('test_description', 'h_A_trump_flush_order', 'joker_A_trump_flush_order'), [
		(
			"1 play: same suit, different nontrump values",
			{'lesser': [Card('s', '2')], 'greater': [Card('s', '5')]},
			{'lesser': [Card('s', '2')], 'greater': [Card('s', '5')]},
		),
		(
			"1 play: trick suit vs lowest suit",
			{'lesser': [Card('d', '5')], 'greater': [Card('s', '5')]},
			{'lesser': [Card('d', '5')], 'greater': [Card('s', '5')]},
		),
		(
			"1 play: h A trump - trick suit vs trump suit; joker A trump - trick suit vs lowest suit",
			{'lesser': [Card('s', '5')], 'greater': [Card('h', '5')]},
			{'lesser': [Card('h', '5')], 'greater': [Card('s', '5')]},
		),
		(
			"1 play: h A trump - trump suit vs trump value; joker A trump - lowest suit vs trump suit",
			{'lesser': [Card('h', '2')], 'greater': [Card('s', 'A')]},
			{'lesser': [Card('h', '2')], 'greater': [Card('s', 'A')]},
		),
		(
			"multiple plays: same suit, all greater values",
			{'lesser': [Card('s', '5'), Card('s', '8')], 'greater': [Card('s', '9'), Card('s', 'Q')]},
			{'lesser': [Card('s', '5'), Card('s', '8')], 'greater': [Card('s', '9'), Card('s', 'Q')]},
		),
		(
			"multiple plays: same suit, highest value of play decides priority",
			{'lesser': [Card('s', '4'), Card('s', '7')], 'greater': [Card('s', '2'), Card('s', '8')]},
			{'lesser': [Card('s', '4'), Card('s', '7')], 'greater': [Card('s', '2'), Card('s', '8')]},
		),
		(
			"multiple plays: h A trump - trump suit vs trick suit, joker A - lowest suit vs trick suit",
			{'lesser': [Card('s', '4'), Card('s', '7')], 'greater': [Card('h', '4'), Card('h', '7')]},
			{'lesser': [Card('h', '4'), Card('h', '7')], 'greater': [Card('s', '4'), Card('s', '7')]},
		),
])
class TestFlushStrengthOrder(unittest.TestCase):
	def testNonJokerTrump(self):
		trick_suit = 's'
		trump_card = Card('h', 'A')
		lesser_flush = Flush(cards_to_tractors(self.h_A_trump_flush_order['lesser'], trick_suit, trump_card))
		greater_flush = Flush(cards_to_tractors(self.h_A_trump_flush_order['greater'], trick_suit, trump_card))
		self.assertLess(lesser_flush, greater_flush)
	def testNonJokerTrump(self):
		trick_suit = 's'
		trump_card = Card('joker', 'A')
		lesser_flush = Flush(cards_to_tractors(self.joker_A_trump_flush_order['lesser'], trick_suit, trump_card))
		greater_flush = Flush(cards_to_tractors(self.joker_A_trump_flush_order['greater'], trick_suit, trump_card))
		self.assertLess(lesser_flush, greater_flush)

@parameterized_class(('test_description', 'h_A_trump_flush_data', 'joker_A_trump_flush_data'), [
		(
			"1 play: same trump value, different nontrump suits",
			{'flush_1': [Card('s', 'A')], 'flush_2': [Card('c', 'A')], 'is_equal': True},
			{'flush_1': [Card('s', 'A')], 'flush_2': [Card('c', 'A')], 'is_equal': True},
		),
		(
			"1 play: same trump value, different trump suit",
			{'flush_1': [Card('s', 'A')], 'flush_2': [Card('h', 'A')], 'is_equal': False},
			{'flush_1': [Card('s', 'A')], 'flush_2': [Card('h', 'A')], 'is_equal': True},
		),
		(
			"multiple plays: same trump value, different trump suits",
			{'flush_1': [Card('s', 'A'), Card('c', 'A')], 'flush_2': [Card('h', 'A'), Card('d', 'A')], 'is_equal': False},
			{'flush_1': [Card('s', 'A'), Card('c', 'A')], 'flush_2': [Card('h', 'A'), Card('d', 'A')], 'is_equal': True},
		),
])
class TestEqualFlush(unittest.TestCase):
	def testNonJokerTrump(self):
		trick_suit = 's'
		trump_card = Card('h', 'A')
		flush_1 = Flush(cards_to_tractors(self.h_A_trump_flush_data['flush_1'], trick_suit, trump_card))
		flush_2 = Flush(cards_to_tractors(self.h_A_trump_flush_data['flush_2'], trick_suit, trump_card))
		self.assertEqual(flush_1 == flush_2, self.h_A_trump_flush_data['is_equal'])
	def testNonJokerTrump(self):
		trick_suit = 's'
		trump_card = Card('joker', 'A')
		flush_1 = Flush(cards_to_tractors(self.joker_A_trump_flush_data['flush_1'], trick_suit, trump_card))
		flush_2 = Flush(cards_to_tractors(self.joker_A_trump_flush_data['flush_2'], trick_suit, trump_card))
		self.assertEqual(flush_1 == flush_2, self.joker_A_trump_flush_data['is_equal'])

class TestTractorMisc(unittest.TestCase):
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

	# this test added due to broken flush comparator in python2.7
	def testFlushComparators(self):
		trick_suit = 's'
		trump_card = Card('h', 'A')

		tests = [
			([Card('d', 'K')],
			 [Card('d', 'K')]),
		]

		for test in tests:
			cards1, cards2 = test
			flush1 = Flush(cards_to_tractors(cards1, trick_suit, trump_card))
			flush2 = Flush(cards_to_tractors(cards2, trick_suit, trump_card))
			self.assertFalse(flush1 > flush2 or flush2 > flush1 or flush1 < flush2 or flush2 < flush1)
			self.assertTrue(flush1 == flush2)

if __name__ == '__main__':
	unittest.main()
