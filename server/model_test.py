import unittest
import mock
from model import *

class TestCard(unittest.TestCase):
	def testDisplaySorted(self):
		trump_card = Card('joker', '2')
		tests = [
			([Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     [Card('h', '3'), Card('s', 'A'), Card('joker', 'big')]),
			([Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
			([Card('d', '8'), Card('c', 'K'), Card('h', '3')],
		     [Card('c', 'K'), Card('d', '8'), Card('h', '3')]),
		    ([Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
		    ([Card('c', 'K'), Card('c', '3'), Card('c', '10')],
		     [Card('c', '3'), Card('c', '10'), Card('c', 'K')]),
		    ([Card('c', '2'), Card('d', '2'), Card('c', '2')],
		     [Card('c', '2'), Card('c', '2'), Card('d', '2')]),
		]

		for test in tests:
			test_list, want = test
			self.assertEqual(display_sorted(test_list, trump_card), want)

	def testIsTrump(self):
		tests = [
			(Card('h','2'), Card('s','3'), False),
			(Card('h','2'), Card('h','3'), True),
			(Card('h','2'), Card('s','2'), True),
		]

		for test in tests:
			trump_card, card, want = test
			self.assertEqual(card.is_trump(trump_card), want)

	def testTrumpSort(self):
		tests = [
			(Card('s', '3'),
			 [Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     [Card('s', 'A'), Card('h', '3'), Card('joker', 'big')]),
			(Card('s', '3'),
			 [Card('joker', 'big'), Card('s', 'A'), Card('s', '3'), Card('h', '3')],
		     [Card('s', 'A'), Card('h', '3'), Card('s', '3'), Card('joker', 'big')]),
			(Card('s', '2'),
			 [Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
			(Card('c', '3'),
			 [Card('c', 'K'), Card('d', '8'), Card('h', '3')],
		     [Card('d', '8'), Card('c', 'K'), Card('h', '3')]),
		    (Card('h', '3'),
		     [Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
		    (Card('d', '2'),
		     [Card('c', 'K'), Card('c', '2'), Card('c', '10')],
		     [Card('c', '10'), Card('c', 'K'), Card('c', '2')])
		]
		for test in tests:
			trump_card, test_list, want = test
			self.assertEqual(display_sorted(test_list, trump_card), want)

class TestRound(unittest.TestCase):
	num_players = 4

	def testFirstPlayerSetToBottomPlayer(self):
		num_decks = 2
		first_player = 0
		third_player = 2
		# Mock model.create_random_deck to use a deterministic deck.
		with mock.patch('model.create_random_deck', return_value=create_deck(num_decks)):
			round = Round(TestRound.num_players)
		self.assertEqual(round.state.turn, first_player)
		# Deal out all cards.
		for _ in range(len(round.state.deck)):
			round.tick()
		# After dealing out all cards, the turn should return to the first player.
		self.assertEqual(round.state.turn, first_player)
		# Have the third player declare the 2 of diamonds.
		round.declare(third_player, [Card('d', '2')])
		# This tick allows for the player to receive the bottom cards.
		round.tick()
		round.set_bottom(third_player, 
			[Card('d', '4'), Card('d', '6'), Card('d', '8'), Card('d', '10'),
			 Card('c', '3'), Card('c', '5'), Card('c', '7'), Card('c', '9')])
		# After setting the bottom, it should now be the third player's turn.
		self.assertEqual(round.state.turn, third_player)

	def testFirstPlayValidity(self):
		round_state = RoundState(TestRound.num_players)
		invalid_play_tests = [
			# 2 singles
			[Card('d', '2'), Card('h', '3')],

			# 1 pair + 1 single
			[Card('d', '2'), Card('d', '2'), Card('s', '5')],

			# 2 nonconsecutive pairs 
			[Card('h', '3'), Card('h', '3'), Card('h', '5'), Card('h', '5')],

			# 2 consecutive pairs + single
			[Card('d', '2'), Card('d', '2'), Card('d', '3'), Card('d', '3'), Card('c', '5')],

			# 2 consecutive pairs + pair
			[Card('d', '2'), Card('d', '2'), Card('d', '3'), Card('d', '3'), Card('s', '5'), Card('s', '5')]
		]

		for test in invalid_play_tests:
			self.assertTrue(round_state.is_first_play_invalid(test))
		
		round_state.trump_card = Card('c', '3')
		valid_play_tests = [
			# 1 single
			[Card('h', '2')],

			# 1 pair
			[Card('s', '2'), Card('s', '2')],

			# 2 consecutive pairs after accounting for trump value
			[Card('c', '2'), Card('c', '2'), Card('c', '4'), Card('c', '4')],

			# 2 consecutive pairs
			[Card('c', '4'), Card('c', '4'), Card('c', '5'), Card('c', '5')],

			# 3 consecutive pairs
			[Card('d', '2'), Card('d', '2'), Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5')]
		]

		for test in valid_play_tests:
			self.assertFalse(round_state.is_first_play_invalid(test))	

if __name__ == '__main__':
	unittest.main()