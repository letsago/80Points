import unittest
import mock
from model import *

class TestCard(unittest.TestCase):
	def testIsTrump(self):
		tests = [
			(Card('h','2'), Card('s','3'), False),
			(Card('h','2'), Card('h','3'), True),
			(Card('h','2'), Card('s','2'), True),
		]

		for test in tests:
			trump_card, card, want = test
			self.assertEqual(card.is_trump(trump_card), want)

	def testDisplaySorted(self):
		tests = [
			(
				Card('joker', '2'),
				[Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     	[Card('h', '3'), Card('s', 'A'), Card('joker', 'big')]
			),

			(	
				Card('joker', '2'),
				[Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

			(
				Card('joker', '2'),
				[Card('d', '8'), Card('c', 'K'), Card('h', '3')],
		     	[Card('c', 'K'), Card('d', '8'), Card('h', '3')]
			),

			(
				Card('joker', '2'),
				[Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

			(
				Card('joker', '2'),
				[Card('c', 'K'), Card('c', '3'), Card('c', '10')],
		     	[Card('c', '3'), Card('c', '10'), Card('c', 'K')]
			),

			(
				Card('joker', '2'),
				[Card('c', '2'), Card('d', '2'), Card('c', '2')],
		     	[Card('c', '2'), Card('c', '2'), Card('d', '2')]
			),

			(
				Card('s', '3'),
			 	[Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     	[Card('s', 'A'), Card('h', '3'), Card('joker', 'big')]
			),

			(	
				Card('s', '3'),
				[Card('joker', 'big'), Card('s', 'A'), Card('s', '3'), Card('h', '3')],
		     	[Card('s', 'A'), Card('h', '3'), Card('s', '3'), Card('joker', 'big')]
			),

			(	
				Card('s', '2'),
				[Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

			(
				Card('c', '3'),
				[Card('c', 'K'), Card('d', '8'), Card('h', '3')],
		     	[Card('d', '8'), Card('c', 'K'), Card('h', '3')]
			),

		    (
				Card('h', '3'),
		     	[Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

		    (
				Card('d', '2'),
		     	[Card('c', 'K'), Card('c', '2'), Card('c', '10')],
		     	[Card('c', '10'), Card('c', 'K'), Card('c', '2')]
			)
		]
		for test in tests:
			trump_card, test_list, want = test
			self.assertEqual(display_sorted(test_list, trump_card), want)

class TestRound(unittest.TestCase):
	def testFirstPlayerSetToBottomPlayer(self):
		num_players = 4
		num_decks = 2
		first_player = 0
		third_player = 2
		# Mock model.create_random_deck to use a deterministic deck.
		with mock.patch('model.create_random_deck', return_value=create_deck(num_decks)):
			round = Round(num_players)
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

class TestRoundState(unittest.TestCase):
	num_players = 4
	round_state = RoundState(num_players)
	first_player = 0

	def testFirstPlayValidity(self):
		invalid_play_tests = [
			# no play
			[],

			# 2 singles
			[Card('d', '2'), Card('h', '3')],

			# 1 pair + 1 single
			[Card('d', '2'), Card('d', '2'), Card('s', '5')],

			# 2 nonconsecutive pairs 
			[Card('h', '3'), Card('h', '3'), Card('h', '5'), Card('h', '5')],

			# 2 consecutive pairs + single
			[Card('d', '2'), Card('d', '2'), Card('d', '3'), Card('d', '3'), Card('c', '5')],

			# 2 pairs in different suits
			[Card('d', '4'), Card('d', '4'), Card('h', '5'), Card('h', '5')],

			# 2 consecutive pairs + pair
			[Card('d', '2'), Card('d', '2'), Card('d', '3'), Card('d', '3'), Card('s', '5'), Card('s', '5')]
		]

		for test in invalid_play_tests:
			self.assertTrue(TestRoundState.round_state.is_play_invalid(first_player, test))
		
		TestRoundState.round_state.trump_card = Card('c', '3')
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
			self.assertFalse(TestRoundState.round_state.is_play_invalid(first_player, test))

	def testFollowSuitValidity(self):
		second_player = 1
		TestRoundState.round_state.trump_card = Card('c', '8')
		TestRoundState.round_state.player_hands[second_player] = [
			Card('s', '4'), Card('s', '5'), Card('s', '5'), Card('s', '10'), Card('s', 'K'), # spades
			Card('h', '5'), # hearts
			Card('h', '8'), Card('s', '8'), Card('s', '8'), Card('c', '8'), Card('c', '8'), Card('joker', 'small') # trump
		]

		invalid_play_tests = [
			# single - doesn't follow suit type
			([Card('s', '3')], [Card('h', '5')]),

			# single - number of cards not equal
			([Card('s', '3')], [Card('s', '5'), Card('s', '5')]),

			# single - number of cards not equal
			([Card('h', '8'), Card('h', '8')], [Card('s', '8')]),

			# pair - must play last same suit pair in hand
			([Card('s', '2'), Card('s', '2')], [Card('s', '4'), Card('s', '5')]),

			# pair - same trump suit, must break in-hand tractor if no other pairs
			([Card('d', '8'), Card('d', '8')], [Card('h', '8'), Card('joker', 'small')]),

			# pair - not out of hearts
			([Card('h', '2'), Card('h', '2')], [Card('s', '8'), Card('s', '8')]),

			# tractor - not out of hearts
			([Card('h', '2'), Card('h', '2'), Card('h', '3'), Card('h', '3')], [Card('s', '8'), Card('s', '8'), Card('c', '8'), Card('c', '8')]),

			# tractor - still have a same suit tractor in hand
			([Card('c', '2'), Card('c', '2'), Card('c', '3'), Card('c', '3')], [Card('h', '8'), Card('s', '8'), Card('s', '8'), Card('joker', 'small')]),

			# tractor - tractors force out same suit pairs
			([Card('s', '2'), Card('s', '2'), Card('s', '3'), Card('s', '3')], [Card('s', '5'), Card('s', '4'), Card('s', '10'), Card('s', 'K')])
		]

		for test in invalid_play_tests:
			first_play, other_play = test
			TestRoundState.round_state.board[0] = first_play
			self.assertTrue(TestRoundState.round_state.is_play_invalid(second_player, other_play))

		valid_play_tests = [
			# single - same nontrump suit
			([Card('s', '3')], [Card('s', '5')]),

			# single - same trump suit
			([Card('c', '8')], [Card('joker', 'small')]),

			# single - same trump suit
			([Card('s', '8')], [Card('h', '8')]),

			# single - out of diamonds, can play anything
			([Card('d', '2')], [Card('s', '4')]),

			# pair - same trump suit, must break in hand tractor if no other pairs
			([Card('d', '8'), Card('d', '8')], [Card('s', '8'), Card('s', '8')]),

			# pair - same nontrump suit
			([Card('s', '2'), Card('s', '2')], [Card('s', '5'), Card('s', '5')]),

			# pair - must play last heart
			([Card('h', '2'), Card('h', '2')], [Card('h', '5'), Card('s', '4')]),

			# tractor - out of diamonds, can play any 4 cards
			([Card('d', '2'), Card('d', '2'), Card('d', '3'), Card('d', '3')], [Card('h', '5'), Card('s', '4'), Card('c', '8'), Card('c', '8')]),

			# tractor - must play same suit tractor in hand
			([Card('c', '2'), Card('c', '2'), Card('c', '3'), Card('c', '3')], [Card('s', '8'), Card('s', '8'), Card('c', '8'), Card('c', '8')]),
			
			# tractor - must play last heart in hand
			([Card('h', '2'), Card('h', '2'), Card('h', '3'), Card('h', '3')], [Card('h', '5'), Card('s', '4'), Card('s', '5'), Card('s', '5')]),

			# tractor - if no same suit tractors, must play same suit pairs
			([Card('s', '2'), Card('s', '2'), Card('s', '3'), Card('s', '3')], [Card('s', '5'), Card('s', '5'), Card('s', '10'), Card('s', 'K')])
		]

		# note all these tests will fail for now since is_play_invalid currently returns True by default
		for test in valid_play_tests:
			first_play, second_play = test
			TestRoundState.round_state.board[0] = first_play
			self.assertFalse(TestRoundState.round_state.is_play_invalid(second_player, second_play))
		 

if __name__ == '__main__':
	unittest.main()