import unittest
from model import Card, CARD_VALUES
from tractor import *
from test_utils import Many, Straight, Double, cards_from_str
from parameterized import parameterized_class, parameterized

from tractor_test_data import cards_to_tractors_test_data, no_trick_test_data

# TODO(workitem0040): test card_to_suit_type function so data['suit_type'] no longer needs to be hardcoded
# TODO(workitem0042): add tractor sorting tests in order to sort tractors in tractor_generator and reduce common output
def tractor_generator(tractors, trump_card):
	return [Tractor(data['rank'], data['length'], data['power_card'].suit_power(trump_card), data['suit_type']) for data in tractors]

@parameterized_class(('test_description', 'test_cards', 's_8_trump_tractor_data', 'joker_8_trump_tractor_data'), cards_to_tractors_test_data)
class TestCardsToTractors(unittest.TestCase):
	# trick suit always 'c' by design because testing cards_to_tractors output and not comparable tractor strength
	def setUp(self):
		self.trick_suit = 'c'

	def testNonJokerTrump(self):
		trump_card = Card('s', '8')
		want = tractor_generator(self.s_8_trump_tractor_data, trump_card)
		self.assertEqual(cards_to_tractors(self.test_cards, self.trick_suit, trump_card), want)

	def testJokerTrump(self):
		# Card('joker', '8') object represents the trump suit and value, not an actual card
		trump_card = Card('joker', '8')
		want = tractor_generator(self.joker_8_trump_tractor_data, trump_card)
		self.assertEqual(cards_to_tractors(self.test_cards, self.trick_suit, trump_card), want)

@parameterized_class(('test_description', 'test_cards', 'tractor_data'), no_trick_test_data)
class TestCardsToTractorsNoTrick(unittest.TestCase):
	def testCardsToTractors(self):
		trump_card = Card('s', '2')
		test_cards = cards_from_str(self.test_cards)
		want = tractor_generator(self.tractor_data, trump_card)
		self.assertEqual(cards_to_tractors(test_cards, None, trump_card), want)

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
	def setUp(self):
		self.trick_suit = 's'

	def testNonJokerTrump(self):
		trump_card = Card('h', 'A')
		lesser_flush = Flush(cards_to_tractors(self.h_A_trump_flush_order['lesser'], self.trick_suit, trump_card))
		greater_flush = Flush(cards_to_tractors(self.h_A_trump_flush_order['greater'], self.trick_suit, trump_card))
		self.assertLess(lesser_flush, greater_flush)

	def testJokerTrump(self):
		trump_card = Card('joker', 'A')
		lesser_flush = Flush(cards_to_tractors(self.joker_A_trump_flush_order['lesser'], self.trick_suit, trump_card))
		greater_flush = Flush(cards_to_tractors(self.joker_A_trump_flush_order['greater'], self.trick_suit, trump_card))
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
	def setUp(self):
		self.trick_suit = 's'

	def testNonJokerTrump(self):
		trump_card = Card('h', 'A')
		flush_1 = Flush(cards_to_tractors(self.h_A_trump_flush_data['flush_1'], self.trick_suit, trump_card))
		flush_2 = Flush(cards_to_tractors(self.h_A_trump_flush_data['flush_2'], self.trick_suit, trump_card))
		self.assertEqual(flush_1 == flush_2, self.h_A_trump_flush_data['is_equal'])

	def testJokerTrump(self):
		trump_card = Card('joker', 'A')
		flush_1 = Flush(cards_to_tractors(self.joker_A_trump_flush_data['flush_1'], self.trick_suit, trump_card))
		flush_2 = Flush(cards_to_tractors(self.joker_A_trump_flush_data['flush_2'], self.trick_suit, trump_card))
		self.assertEqual(flush_1 == flush_2, self.joker_A_trump_flush_data['is_equal'])

class TestTractorMatchForm(unittest.TestCase):
	trump_card = Card('s', 'A')

	# trick suit always 'd', trump suit always 's'
	@parameterized.expand([
			(
				# player1 plays triple, double, double in trick suit
				# player2 plays quadruple, triple in trump suit
				Many('d', '2', rank=3) + Double('d', '4') + Double('d', '6'),
				Many('s', '2', rank=4) + Many('s', '4', rank=3),
				[Tractor(2, 1, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
				 Tractor(2, 1, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
				 Tractor(3, 1, Card('s', '4').suit_power(trump_card), SUIT_TRUMP)],
			), (
				# player1 plays triple, double, double in trick suit
				# player2 plays triple, triple, single in trump suit
				Many('d', '2', rank=3) + Double('d', '4') + Double('d', '6'),
				Many('s', '2', rank=3) + Many('s', '4', rank=3) + [Card('s', '6')],
				None,
			), (
				#player1 plays double,double,double; triple,triple; triple in trick suit
				#player2 plays triple,triple,triple; double,double,double in trump suit
				Many('d', '2', rank=2, length=3) + Many('d', '6', rank=3, length=2) + Many('d', '9', rank=3, length=1),
				Many('s', '2', rank=3, length=3) + Many('s', '6', rank=2, length=3),
				[Tractor(2, 3, Card('s', '6').suit_power(trump_card), SUIT_TRUMP),
				 Tractor(3, 1, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
				 Tractor(3, 2, Card('s', '2').suit_power(trump_card), SUIT_TRUMP)],
			), (
				#player1 plays double,double,double; triple,triple; triple in trick suit
				#player2 plays triple,triple,triple; triple,triple in trump suit
				Many('d', '2', rank=2, length=3) + Many('d', '6', rank=3, length=2) + Many('d', '9', rank=3, length=1),
				Many('s', '2', rank=3, length=3) + Many('s', '6', rank=3, length=2),
				None,
			), (
				#player1 plays double,double; double;double; double; double in trick suit
				#player2 plays quadruple;quadruple;quadruple in trump suit
				Many('d', '2', rank=2, length=2) + Many('d', '5', rank=2, length=2) + Double('d', '8') + Double('d', 'J'),
				Many('s', '2', rank=4, length=3),
				[Tractor(2, 1, Card('s', '4').suit_power(trump_card), SUIT_TRUMP),
				 Tractor(2, 1, Card('s', '4').suit_power(trump_card), SUIT_TRUMP),
				 Tractor(2, 2, Card('s', '2').suit_power(trump_card), SUIT_TRUMP),
				 Tractor(2, 2, Card('s', '2').suit_power(trump_card), SUIT_TRUMP)],
			),
	])

	def testCardsToTractorsWithForm(self, start_cards, cur_cards, want_tractors):
		trick_suit = 'd'
		target_form = cards_to_tractors(start_cards, trick_suit, TestTractorMatchForm.trump_card)
		got_tractors = cards_to_tractors(cur_cards, trick_suit, TestTractorMatchForm.trump_card, target_form=target_form)
		self.assertEqual(got_tractors, want_tractors)

class TestTractorMisc(unittest.TestCase):
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

	@parameterized.expand([
		[
			'same rank and length',
			[TractorMetadata(3, 2)],
			TractorMetadata(3, 2),
			[]
		],
		[
			'same rank, different length',
			[TractorMetadata(2, 2)],
			TractorMetadata(2, 1),
			[TractorMetadata(2, 1)],
		],
		[
			'different rank, same length',
			[TractorMetadata(3, 1)],
			TractorMetadata(2, 1),
			[TractorMetadata(1, 1)],
		],
		[
			'different rank and length',
			[TractorMetadata(3, 2)],
			TractorMetadata(1, 1),
			[TractorMetadata(3, 1), TractorMetadata(2, 1)],
		],
		[
			'different rank and length, multiple (1, 1) tractor decomposition',
			[TractorMetadata(3, 3)],
			TractorMetadata(2, 2),
			[TractorMetadata(3, 1), TractorMetadata(1, 1), TractorMetadata(1, 1)],
		],
	])

	# data_to_remove rank and length is asserted to be less than or equal to at least one data element in data_array
	def testUpdateTractorDataArray(self, name, data_array, data_to_remove, expected_output):
		self.assertEqual(update_data_array(data_array, data_to_remove), expected_output)

if __name__ == '__main__':
	unittest.main()
