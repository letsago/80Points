import unittest
import mock
from model import *
from parameterized import parameterized
from tractor_test import tractor_generator
from tractor import SUIT_LOWEST, SUIT_TRICK, SUIT_TRUMP 
from model_test_data import follow_suit_validity_test_data

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
	# TODO(workitem0028): will add flush validation tests once flush capability is integrated
	def setUp(self):
		self.num_players = 6
		self.first_player = 0
		self.second_player = 1
		self.round_state = RoundState(self.num_players)
		self.round_state.trump_card = Card('c', '3')
		self.round_state.player_hands[self.second_player] = [
			Card('s', '4'), Card('s', '5'), Card('s', '5'), Card('s', '10'), Card('s', 'K'), # spades
			Card('h', '5'), # hearts
			Card('c', '8'), Card('c', '8'), Card('c', '8'), Card('h', '3'), Card('s', '3'), Card('s', '3'), # trump
			Card('c', '3'), Card('c', '3'), Card('joker', 'small'), Card('joker', 'small') # trump
		]

	@parameterized.expand([
		['diamonds', 'd', []],
		['hearts', 'h', [
			{'rank': 1, 'length': 1, 'power_card': Card('h', '5'), 'suit_type': SUIT_TRICK}]
		],
		['spades', 's', [
			{'rank': 2, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', 'K'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', '10'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_TRICK}]
		],
		['trump', 'c', [
			{'rank': 3, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
			{'rank': 2, 'length': 3, 'power_card': Card('s', '3'), 'suit_type': SUIT_TRUMP},
			{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_TRUMP}]
		],
	])
	
	@unittest.skip('get_tractors_from_hand function is not properly functioning yet')
	def testSuitTractorsFromHand(self, suit_name, trick_suit, suit_tractors):
		trump_card = self.round_state.trump_card
		self.assertEqual(self.round_state.get_suit_tractors(self.second_player, trick_suit, trump_card), suit_tractors)

	@parameterized.expand([
		['no play', []],

		['different suits 2 singles', [Card('d', '2'), Card('h', '3')]],

		['different suits 1 pair + 1 single', [Card('d', '2'), Card('d', '2'), Card('s', '5')]],

		['same suits 2 nonconsecutive pairs', [Card('h', '2'), Card('h', '2'), Card('h', '6'), Card('h', '6')]],

		['different suits 2 consecutive pairs + single', 
			[Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5'), Card('c', '5')]],

		['different suits 2 nonconsecutive pairs', 
			[Card('d', '4'), Card('d', '4'), Card('h', '5'), Card('h', '5')]],
			
		['different suits 2 consecutive pairs + pair', 
			[Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5'), Card('s', '7'), Card('s', '7')]],
	])

	def testInvalidFirstPlays(self, name, play):
		self.assertFalse(self.round_state.is_play_valid(self.first_player, play))
	
	@parameterized.expand([
		['1 single', [Card('h', '2')]],

		['same suit 1 pair', [Card('s', '2'), Card('s', '2')]],

		['same suit 2 consecutive pairs considering trump value', 
			[Card('c', '2'), Card('c', '2'), Card('c', '4'), Card('c', '4')]],

		['same suit 2 consecutive pairs', 
			[Card('c', '4'), Card('c', '4'), Card('c', '5'), Card('c', '5')]],

		['same suit 3 consecutive pairs considering trump value', 
			[Card('d', '2'), Card('d', '2'), Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5')]],

		['same suit 3 consecutive pairs', 
			[Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5'), Card('d', '6'), Card('d', '6')]],
	])

	def testValidFirstPlays(self, name, play):
		self.assertTrue(self.round_state.is_play_valid(self.first_player, play))
		
	@parameterized.expand(follow_suit_validity_test_data)

	# will remove skipping this test once is_play_valid function is fully built
	@unittest.skip('is_play_valid function is not properly functioning yet')
	def testFollowSuitValidity(self, name, first_play, invalid_play, valid_play):
		self.round_state.board[0] = first_play
		self.assertFalse(self.round_state.is_play_valid(second_player, invalid_play))
		self.assertTrue(self.round_state.is_play_valid(second_player, valid_play))

if __name__ == '__main__':
	unittest.main()